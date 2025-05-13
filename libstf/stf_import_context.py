from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STFReportSeverity, STFReport


class STF_ImportContext:
	"""Context for top level resource import"""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._tasks: list[Callable] = []

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
						self.register_imported_resource(component_id, application_component_object)
					else:
						self.report(STFReport("Component import error", STFReportSeverity.Error, component_id, json_component.get("type"), application_object))
				else:
					self.report(STFReport("No STF_Module registered for component", STFReportSeverity.Warn, component_id, json_component.get("type")))


	def import_resource(self, stf_id: str, context_object: any = None, stf_kind: str = "data") -> any:
		if(stf_id in self._state._imported_resources):
			return self._state._imported_resources[stf_id]

		json_resource = self.get_json_resource(stf_id)
		if(not json_resource or type(json_resource) is not dict or "type" not in json_resource):
			self.report(STFReport("Invalid JSON resource", STFReportSeverity.FatalError, stf_id))

		if(module := self._state.determine_module(json_resource, stf_kind)):
			application_object = module.import_func(self, json_resource, stf_id, context_object)
			if(application_object):
				self.__run_components(json_resource, module.get_components_holder_func(application_object) if hasattr(module, "get_components_holder_func") else application_object)

				self.register_imported_resource(stf_id, application_object)
				return application_object
			else:
				self.report(STFReport("Resource import error", STFReportSeverity.Error, stf_id, module.stf_type, None))
		else:
			# TODO json fallback
			self.report(STFReport("No STF_Module registered", STFReportSeverity.Warn, stf_id, json_resource.get("type")))
		return None


	def import_buffer(self, stf_id: str) -> bytes:
		return self._state.import_buffer(stf_id)


	def resolve_stf_property_path(self, stf_path: list[str], application_object: any = None) -> tuple[any, int, any, str, int, Callable[[any], any]]:
		if(stf_path == None or len(stf_path) == 0): return None

		if(selected_module := self._state.determine_property_resolution_module(stf_path[0])):
			return selected_module.resolve_stf_property_to_blender_func(self, stf_path, application_object)

		return None


	def add_task(self, task: Callable):
		self._state._tasks.append(task)

	def get_root_id(self) -> str:
		return self._state._file.definition.stf.root

	def get_filename(self) -> str:
		return self._state._file.filename

	def get_root_context(self) -> any:
		return self

	def report(self, report: STFReport):
		self._state.report(report)
