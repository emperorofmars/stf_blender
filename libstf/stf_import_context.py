import io
from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STF_Report_Severity, STFReport
from .stf_module import STF_ImportHook


class STF_RootImportContext:
	"""Context for top level resource import"""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._tasks: list[Callable] = []

	def get_json_resource(self, id: str) -> dict:
		return self._state.get_json_resource(id)

	def get_parent_application_object(self) -> any:
		return None

	def import_resource(self, id: str) -> any:
		if(id in self._state._imported_resources.keys()): return self._state._imported_resources[id]

		json_resource = self.get_json_resource(id)
		if(not json_resource or type(json_resource) is not dict or "type" not in json_resource):
			self.report(STFReport("Invalid JSON resource", STF_Report_Severity.FatalError, id))

		if(module := self._state.determine_module(json_resource)):
			accepted_hooks: list[tuple[STF_ImportHook, dict, str]] = []
			if(hooks := self._state.determine_hooks(json_resource)):
				for hook in hooks:
					can_handle, hook_json_resource, hook_resource_id = hook.hook_can_handle_stf_object_func(json_resource)
					if(can_handle):
						accepted_hooks.append((hook, hook_json_resource, hook_resource_id))

			hook_results = []
			for hook, hook_json_resource, hook_resource_id in accepted_hooks:
				hook_result = hook.import_func(self, hook_json_resource, hook_resource_id, None, None)
				if(hook_result):
					hook_results.append(hook_result)
				else:
					self.report(STFReport("Hook execution error", STF_Report_Severity.Error, hook_resource_id, hook.stf_type))

			application_object = module.import_func(self, json_resource, id, self.get_parent_application_object(), hook_results)

			# TODO components

			return application_object
		else:
			# TODO json fallback
			self.report(STFReport("No STF_Module registered", STF_Report_Severity.Warn, id, json_resource["type"]))
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
