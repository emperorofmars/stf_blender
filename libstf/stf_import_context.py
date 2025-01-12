import io
from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STFReportSeverity, STFReport


class STF_RootImportContext:
	"""Context for top level resource import"""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._tasks: list[Callable] = []

	def get_json_resource(self, id: str) -> dict:
		return self._state.get_json_resource(id)

	def get_parent_application_object(self) -> any:
		return None

	def get_imported_resource(self, id: str):
		return self._state.get_imported_resource(id)

	def register_imported_resource(self, id: str, application_object: any):
		self._state.register_imported_resource(id, application_object)


	def __run_components(self, json_resource: dict, application_object: any, context: any):
		if("components" in json_resource):
			for component_id, json_component in json_resource["components"].items():
				if(component_module := self._state.determine_module(json_component)):
					component_result = component_module.import_func(context, json_component, component_id, application_object, None)
					if(component_result):
						application_component_object, _ = component_result
						self.register_imported_resource(component_id, application_component_object)
					else:
						self.report(STFReport("Component import error", STFReportSeverity.Error, component_id, json_component.get("type"), application_object))
				else:
					self.report(STFReport("No STF_Module registered for component", STFReportSeverity.Warn, component_id, json_component.get("type")))


	def import_resource(self, id: str) -> any:
		if(id in self._state._imported_resources.keys()): return self._state._imported_resources[id]

		json_resource = self.get_json_resource(id)
		if(not json_resource or type(json_resource) is not dict or "type" not in json_resource):
			self.report(STFReport("Invalid JSON resource", STFReportSeverity.FatalError, id))

		if(module := self._state.determine_module(json_resource)):
			module_ret = module.import_func(self, json_resource, id, self.get_parent_application_object())
			if(module_ret):
				application_object, context = module_ret
			else:
				self.report(STFReport("Resource import error", STFReportSeverity.Error, id, module.stf_type, None))

			self.__run_components(json_resource, application_object, context)

			self.register_imported_resource(id, application_object)
			return application_object
		else:
			# TODO json fallback
			self.report(STFReport("No STF_Module registered", STFReportSeverity.Warn, id, json_resource.get("type")))
		return None


	def import_buffer(self, id: str) -> io.BytesIO:
		return self._state.import_buffer(id)


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


class STF_ResourceImportContext(STF_RootImportContext):
	"""
		Context for the import of sub-resources.

		Extend this class if you need a custom context for sub-resources.
	"""

	def __init__(self, parent_context: STF_RootImportContext, json_resource: dict, parent_application_object: any):
		super().__init__(parent_context._state)
		self._parent_context = parent_context
		self._json_resource = json_resource
		self._parent_application_object = parent_application_object

	def get_parent_application_object(self) -> any:
		return self._parent_application_object

	def get_root_context(self) -> any:
		return self._parent_context.get_root_context()
