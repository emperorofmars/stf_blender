import bpy
import logging
from typing import Callable

from ..base.stf_task_steps import STF_TaskSteps
from .stf_import_state import STF_ImportState
from ..base.stf_report import STFReportSeverity, STFReport
from ..base.stf_module_component import STF_Component_Editmode_Resistant_Reference
from ..base.property_path_part import BlenderPropertyPathPart


_logger = logging.getLogger(__name__)


class STF_ImportContext:
	"""Context for top level resource import"""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._root_collection = None
		#self._tasks: list[Callable] = []

	def get_json_resource(self, stf_id: str) -> dict:
		return self._state.get_json_resource(stf_id)

	def get_imported_resource(self, stf_id: str):
		return self._state.get_imported_resource(stf_id)

	def register_imported_resource(self, stf_id: str, application_object: any):
		self._state.register_imported_resource(stf_id, application_object)


	def __run_components(self, json_resource: dict, application_object: any):
		if("components" in json_resource):
			for component_id in json_resource["components"]:
				json_component = self.get_json_resource(component_id)
				if(component_module := self._state.determine_module(json_component, "component")):
					component_result = component_module.import_func(self, json_component, component_id, application_object)
					if(component_result):
						application_component_object = component_result
						self.register_imported_resource(component_id, STF_Component_Editmode_Resistant_Reference(application_component_object, application_object))
					else:
						_logger.error("Component import error", stack_info=True)
						self.report(STFReport("Component import error", STFReportSeverity.Error, component_id, json_component.get("type"), application_object))
				else:
					self.report(STFReport("No STF_Module registered for component", STFReportSeverity.Warn, component_id, json_component.get("type")))


	def import_resource(self, stf_id: str, context_object: any = None, stf_kind: str = "data") -> any:
		if(stf_id in self._state._imported_resources):
			if(type(self._state._imported_resources[stf_id]) == STF_Component_Editmode_Resistant_Reference):
				return self._state._imported_resources[stf_id].get()
			else:
				return self._state._imported_resources[stf_id]

		json_resource = self.get_json_resource(stf_id)
		if(not json_resource or type(json_resource) is not dict or "type" not in json_resource):
			_logger.fatal("Invalid JSON resource", stack_info=True)
			self.report(STFReport("Invalid JSON resource", STFReportSeverity.FatalError, stf_id, application_object=context_object))

		if(module := self._state.determine_module(json_resource, stf_kind)):
			application_object = module.import_func(self, json_resource, stf_id, context_object)
			if(application_object):
				self.register_imported_resource(stf_id, application_object)
				self.__run_components(json_resource, module.get_components_holder_func(application_object) if hasattr(module, "get_components_holder_func") else application_object)
				return application_object
			else:
				_logger.error("Resource import error", stack_info=True)
				self.report(STFReport("Resource import error", STFReportSeverity.Error, stf_id, module.stf_type, None))
		else:
			self.report(STFReport("Could not process resource: " + stf_id, STFReportSeverity.FatalError, stf_id, json_resource.get("type")))
		return None


	def import_buffer(self, stf_id: str) -> bytes:
		return self._state.import_buffer(stf_id)


	def resolve_stf_property_path(self, stf_path: list[str], application_object: any = None) -> BlenderPropertyPathPart:
		if(stf_path == None or len(stf_path) == 0): return None

		if(selected_module := self._state.determine_property_resolution_module(stf_path[0])):
			return selected_module.resolve_stf_property_to_blender_func(self, stf_path, application_object)

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

	def get_filename(self) -> str:
		return self._state._file.filename

	def report(self, report: STFReport):
		self._state.report(report)
