import bpy
import logging
from typing import Callable

from ..base.property_path_part import STFPropertyPathPart

from ..base.stf_task_steps import STF_TaskSteps
from .stf_export_state import STF_ExportState
from ..base.stf_definition import STF_Meta_AssetInfo
from ..base.stf_report import STFReportSeverity, STFReport


_logger = logging.getLogger(__name__)


class STF_ExportContext:
	"""Context for resource export. It will be passed to each STF_Module's export func."""

	def __init__(self, state: STF_ExportState, prefab: bpy.types.Collection):
		self._state = state
		self._prefab = prefab

	def run(self) -> str:
		root_id = self.serialize_resource(self._prefab)
		self._state.set_root_id(root_id)
		self._state.run_tasks()
		return root_id


	def get_resource_id(self, application_object: any) -> str | None:
		return self._state.get_resource_id(application_object)

	def register_id(self, application_object: any, stf_id: str):
		self._state.register_id(application_object, stf_id)


	def __run_hooks(self, application_object: any, context_object: any, json_resource: dict, stf_id: str):
		"""Run hooks on application object"""
		if(hooks := self._state.determine_hooks(application_object)):
			for hook in hooks:
				if(hook.hook_can_handle_application_object_func(application_object)):
					if("components" not in json_resource): json_resource["components"] = []
					hook.hook_apply_func(self, application_object, context_object)


	def __run_components(self, application_object: any, json_resource: dict, stf_id: str, components: list):
		"""Export components explicitely defined by this application"""
		if(len(components) > 0):
			if("components" not in json_resource): json_resource["components"] = []
			for component in components:
				if(selected_module := self._state.determine_module(component, "component")):
					component_ret = selected_module.export_func(self, component, application_object)
					if(component_ret):
						component_json_resource, component_id = component_ret
						self._state.register_serialized_resource(component, component_json_resource, component_id)
						json_resource["components"].append(component_id)
					else:
						_logger.error("Export Component Failed", stack_info=True)
						self.report(STFReport("Export Component Failed", STFReportSeverity.Error, stf_id, selected_module.stf_type, application_object))
				else:
					self.report(STFReport("Unsupported Component", STFReportSeverity.Warn, None, None, application_object))


	def serialize_resource(self, application_object: any, context_object: any = None, module_kind = None, export_fail_severity: STFReportSeverity = STFReportSeverity.Error) -> str | None:
		"""Run all logic to serialize an application resource. If it already has been serialized, return the existing ID."""

		if(application_object == None): return None
		if(existing_id := self.get_resource_id(application_object)): return existing_id

		if(selected_module := self._state.determine_module(application_object, module_kind)):
			module_ret = selected_module.export_func(self, application_object, context_object)

			if(module_ret):
				json_resource, resource_id = module_ret
				self._state.register_serialized_resource(application_object, json_resource, resource_id)

				if(selected_module.stf_kind not in ["component", "instance"]):
					# Export components from application native constructs
					self.__run_hooks(application_object, context_object, json_resource, resource_id)

					if(hasattr(selected_module, "get_components_func")):
						# Export components explicitely defined
						components = selected_module.get_components_func(application_object)
						self.__run_components(application_object, json_resource, resource_id, components)

				return resource_id
			else:
				if(export_fail_severity.value >= STFReportSeverity.Error.value):
					_logger.error("Resource Export Failed", stack_info=True)
				self.report(STFReport("Resource Export Failed", export_fail_severity, None, selected_module.stf_type, application_object))
		else:
			if(export_fail_severity.value >= STFReportSeverity.Error.value):
				_logger.error("No Module Found", stack_info=True)
			self.report(STFReport("No Module Found", export_fail_severity, None, None, application_object))
		return None


	def serialize_buffer(self, data: bytes, buffer_id: str = None) -> str:
		return self._state.serialize_buffer(data, buffer_id)


	def resolve_application_property_path(self, application_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
		if(application_object == None): return None
		if(type(application_object) == bpy.types.Object and not self.get_resource_id(application_object)):
			return None

		if(data_path.startswith(".")): data_path = data_path[1:]

		if(selected_module := self._state.determine_property_resolution_module(application_object, data_path)):
			return selected_module.resolve_property_path_to_stf_func(self, application_object, application_object_property_index, data_path)

		return None


	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been exported"""
		self._state.add_task(step, task)

	def add_cleanup_task(self, task: Callable):
		self._state.add_cleanup_task(task)

	def register_trash_object(self, trash: bpy.types.Object):
		self._state._trash_objects.append(trash)


	def get_root(self) -> bpy.types.Collection:
		return self._prefab


	def report(self, report: STFReport):
		self._state.report(report)


	def id_exists(self, stf_id: str) -> bool:
		return self._state.id_exists(stf_id)

	def get_setting(self, key: str, default: any = None) -> any:
		return getattr(self._state._settings, key) if hasattr(self._state._settings, key) else default

	def get_root_id(self) -> str | None:
		return self._state._root_id

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		return self._state._asset_info
