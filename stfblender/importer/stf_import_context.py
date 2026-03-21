import bpy
import logging
from typing import Any, Callable

from ..common import STF_ImportContext as ISTF_ImportContext, STF_Category
from ..common.stf_task_steps import STF_TaskSteps
from .stf_import_state import STF_ImportState
from ..common.stf_report import STFReportSeverity, STFReport
from ..common.resource.component.stf_handler_component import STF_Component_Editmode_Resistant_Reference
from ..common.property_path_part import BlenderPropertyPathPart


_logger = logging.getLogger(__name__)


class STF_ImportContext(ISTF_ImportContext):
	"""Context for resource import. It will be passed to each STF_Module's import func."""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._root_collection = None

	def run(self) -> bpy.types.Collection:
		ret = self._import_resource(self.get_root_id(), STF_Category.DATA)
		if(not ret):
			raise Exception("Failed to export root resource")
		self._state.run_tasks()
		ret.stf_meta.from_stf_meta_assetInfo(self._state._file.definition.stf.asset_info, self._state._file.definition.stf.asset_properties)
		return ret


	def get_json_resource(self, stf_id: str) -> dict[str, Any] | None:
		return self._state.get_json_resource(stf_id)

	def get_imported_resource(self, stf_id: str) -> Any | None:
		return self._state.get_imported_resource(stf_id)

	def register_imported_resource(self, stf_id: str, application_object: Any):
		self._state.register_imported_resource(stf_id, application_object)


	def __run_components(self, json_resource: dict, application_object: Any):
		if("components" in json_resource):
			for component_id in json_resource["components"]:
				if(json_component := self.get_json_resource(component_id)):
					if(component_handler := self._state.determine_handler(json_component, STF_Category.COMPONENT)):
						component_result = component_handler.import_func(self, json_component, component_id, application_object)
						if(component_result and type(component_result) is not STFReport):
							application_component_object = component_result
							self.register_imported_resource(component_id, STF_Component_Editmode_Resistant_Reference(application_component_object, application_object))
						else:
							_logger.error("Component import error", stack_info=True)
							if(type(component_result) is STFReport):
								self.report(component_result)
							else:
								self.report(STFReport("Component import error", STFReportSeverity.Error, component_id, json_component.get("type"), application_object))
					else:
						self.report(STFReport("No STF_Module registered for component", STFReportSeverity.Warn, component_id, json_component.get("type")))
				else:
					self.report(STFReport("Invalid JSON resource", STFReportSeverity.FatalError, component_id))


	def import_resource(self, json_parent: dict, resource_index: int, context_object: Any = None, stf_category: str = STF_Category.DATA) -> Any:
		if(type(resource_index) is str): # todo remove this possibility sometime after stf v0.1.x
			return self._import_resource(resource_index, context_object, stf_category)
		if(resource_index is None or "referenced_resources" not in json_parent or len(json_parent["referenced_resources"]) < resource_index):
			return None
		else:
			return self._import_resource(json_parent["referenced_resources"][resource_index], context_object, stf_category)

	def _import_resource(self, stf_id: str, context_object: Any = None, stf_category: str | None = STF_Category.DATA) -> Any | None:
		if(stf_id in self._state._imported_resources):
			if(type(self._state._imported_resources[stf_id]) is STF_Component_Editmode_Resistant_Reference):
				return self._state._imported_resources[stf_id].get()
			else:
				return self._state._imported_resources[stf_id]

		json_resource = self.get_json_resource(stf_id)
		if(not json_resource or type(json_resource) is not dict or "type" not in json_resource):
			_logger.fatal("Invalid JSON resource", stack_info=True)
			self.report(STFReport("Invalid JSON resource", STFReportSeverity.FatalError, stf_id, application_object=context_object))

		if(handler := self._state.determine_handler(json_resource, stf_category)):
			application_object = handler.import_func(self, json_resource, stf_id, context_object)
			if(application_object and type(application_object) is not STFReport):
				self.register_imported_resource(stf_id, application_object)
				self.__run_components(json_resource, handler.get_components_holder_func(application_object) if hasattr(handler, "get_components_holder_func") else application_object)
				return application_object
			else:
				_logger.error("Resource import error", stack_info=True)
				if(type(application_object) is STFReport):
					self.report(application_object)
				else:
					self.report(STFReport("Resource import error", STFReportSeverity.Error, stf_id, handler.stf_type, None))
		else:
			self.report(STFReport("Could not process resource: " + stf_id, STFReportSeverity.FatalError, stf_id, json_resource.get("type")))
		return None


	def import_buffer(self, json_parent: dict, buffer_index: int) -> bytes | None:
		if(type(buffer_index) is str): # todo remove this possibility sometime after stf v0.1.x
			return self._state.import_buffer(buffer_index)
		if(buffer_index is None or "referenced_buffers" not in json_parent or len(json_parent["referenced_buffers"]) < buffer_index):
			return None
		else:
			return self._state.import_buffer(json_parent["referenced_buffers"][buffer_index])

	def _import_buffer(self, stf_id: str) -> bytes | None:
		return self._state.import_buffer(stf_id)


	def resolve_stf_property_path(self, stf_path: list[str], application_object: Any = None) -> BlenderPropertyPathPart | None:
		if(stf_path is None or len(stf_path) == 0): return None

		if(selected_handler := self._state.determine_property_resolution_handler(stf_path[0])):
			return selected_handler.resolve_stf_property_to_blender_func(self, stf_path, application_object)

		return None


	def add_task(self, step: int | STF_TaskSteps, task: Callable):
		"""Will be executed after all other resources have been exported"""
		self._state.add_task(step, task)

	def add_cleanup_task(self, task: Callable):
		self._state.add_cleanup_task(task)

	def register_trash_object(self, trash: bpy.types.Object):
		self._state._trash_objects.append(trash)

	def get_root_id(self) -> str:
		return self._state._file.definition.stf.root

	def set_root_collection(self, root_collection: bpy.types.Collection):
		self._root_collection = root_collection

	def get_root_collection(self) -> bpy.types.Collection:
		return self._root_collection


	def get_setting(self, key: str, default: Any = None) -> Any:
		return getattr(self._state._settings, key) if hasattr(self._state._settings, key) else default


	def get_filename(self) -> str:
		return self._state._file.filename

	def report(self, report: STFReport):
		self._state.report(report)
