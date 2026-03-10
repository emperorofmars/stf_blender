import bpy
import logging
from typing import Any, Callable

from ..common import STF_ExportContext as ISTF_ExportContext, STF_TaskSteps
from .stf_export_state import STF_ExportState
from ..common.base.stf_json_definition import STF_Meta_AssetInfo
from ..common.stf_report import STFReportSeverity, STFReport
from ..common.property_path_part import STFPropertyPathPart


_logger = logging.getLogger(__name__)


class STF_ExportContext(ISTF_ExportContext):
	"""Context for resource export. It will be passed to each STF_Module's export func."""

	def __init__(self, state: STF_ExportState, prefab: bpy.types.Collection):
		self._state = state
		self._prefab = prefab

	def run(self) -> str:
		root_id = self.serialize_resource(self._prefab)
		self._state.set_root_id(root_id)
		self._state.run_tasks()
		return root_id


	def get_resource_id(self, application_object: Any) -> str | None:
		return self._state.get_resource_id(application_object)

	def register_id(self, application_object: Any, stf_id: str):
		self._state.register_id(application_object, stf_id)


	def __run_hooks(self, application_object: Any, context_object: Any, json_resource: dict, stf_id: str):
		"""Run hooks on application object"""
		if(hooks := self._state.determine_hooks(application_object)):
			for hook in hooks:
				if(hook.hook_can_handle_application_object_func(application_object)):
					if("components" not in json_resource): json_resource["components"] = []
					hook.hook_apply_func(self, application_object, context_object)


	def __run_components(self, application_object: Any, json_resource: dict, stf_id: str, components: list):
		"""Export components explicitely defined by this application"""
		if(len(components) > 0):
			if("components" not in json_resource): json_resource["components"] = []
			for component in components:
				if(selected_handler := self._state.determine_handler(component, "component")):
					component_ret = selected_handler.export_func(self, component, application_object)
					if(component_ret and type(component_ret) is not STFReport):
						component_json_resource, component_id = component_ret
						self._state.register_serialized_resource(component, component_json_resource, component_id)
						json_resource["components"].append(component_id)
					else:
						_logger.error("Export Component Failed", stack_info=True)
						if(type(component_ret) is STFReport):
							self.report(component_ret)
						else:
							self.report(STFReport("Export Component Failed", STFReportSeverity.Error, stf_id, selected_handler.stf_type, application_object))
				else:
					self.report(STFReport("Unsupported Component", STFReportSeverity.Warn, None, None, application_object))


	def serialize_resource(self, application_object: Any, context_object: Any = None, stf_category: str | None = None, export_fail_severity: STFReportSeverity = STFReportSeverity.Error) -> str | None:
		"""Run all logic to serialize an application resource. If it already has been serialized, return the existing ID."""

		if(application_object == None): return None
		if(existing_id := self.get_resource_id(application_object)): return existing_id

		if(selected_handler := self._state.determine_handler(application_object, stf_category)):
			handler_ret = selected_handler.export_func(self, application_object, context_object)

			if(handler_ret and type(handler_ret) is not STFReport):
				json_resource, resource_id = handler_ret
				self._state.register_serialized_resource(application_object, json_resource, resource_id)

				if(selected_handler.stf_category not in ["component", "instance"]):
					# Export components from application native constructs
					self.__run_hooks(application_object, context_object, json_resource, resource_id)

					if(hasattr(selected_handler, "get_components_func")):
						# Export components explicitely defined
						components = selected_handler.get_components_func(application_object)
						self.__run_components(application_object, json_resource, resource_id, components)

				return resource_id
			else:
				if(export_fail_severity.value >= STFReportSeverity.Error.value):
					_logger.error("Resource Export Failed", stack_info=True)
				if(type(handler_ret) is STFReport):
					self.report(handler_ret)
				else:
					self.report(STFReport("Resource Export Failed", export_fail_severity, None, selected_handler.stf_type, application_object))
		else:
			if(export_fail_severity.value >= STFReportSeverity.Error.value):
				_logger.error("No Module Found", stack_info=True)
			self.report(STFReport("No Module Found", export_fail_severity, None, None, application_object))
		return None


	def serialize_buffer(self, data: bytes, buffer_id: str = None) -> str:
		return self._state.serialize_buffer(data, buffer_id)


	def resolve_application_property_path(self, application_object: Any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
		if(application_object == None): return None
		if(type(application_object) == bpy.types.Object and not self.get_resource_id(application_object)):
			return None

		if(data_path.startswith(".")): data_path = data_path[1:]

		if(selected_handler := self._state.determine_property_resolution_handler(application_object, data_path)):
			return selected_handler.resolve_property_path_to_stf_func(self, application_object, application_object_property_index, data_path)

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

	def get_setting(self, key: str, default: Any = None) -> Any:
		return getattr(self._state._settings, key) if hasattr(self._state._settings, key) else default

	def get_root_id(self) -> str | None:
		return self._state._root_id

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		return self._state._asset_info
