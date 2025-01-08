import io
from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STF_Report_Severity, STFReport


class STF_RootImportContext:
	"""Context for top level resource import"""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._tasks: list[Callable] = []

	def import_resource(self, id: str) -> any:
		if(id in self._state._imported_resources.keys()): return self._state._imported_resources[id]

		json_resource = self.get_json_resource(id)
		if(not json_resource or type(json_resource) is not dict or "type" not in json_resource):
			self.report(STFReport("Invalid JSON resource", STF_Report_Severity.FatalError, id))

		if(hooks := self._state.determine_hooks(json_resource)):
			pass
		elif(module := self._state.determine_module(json_resource)):
			return module.import_func(self, json_resource, id)
		else:
			pass # TODO json fallback
		return None

	def import_buffer(self, id: str) -> io.BytesIO:
		return self._state.import_buffer(id)

	def add_task(self, task: Callable):
		self._state._tasks.append(task)

	def get_json_resource(self, id: int) -> dict:
		return self._state.get_json_resource(id)

	def get_root_id(self) -> str:
		return self._state._file.definition.stf.root

	def get_filename(self) -> str:
		return self._state._file.filename

	def get_root_context(self) -> any:
		return self

	def report(self, report: STFReport):
		self._state.report(report)


class STF_ResourceExportContext(STF_RootImportContext):
	"""
		Context for the import of sub-resources.

		Extend this class if you need a custom context for sub-resources.
	"""

	def __init__(self, parent_context: STF_RootImportContext, json_resource: dict):
		super().__init__(parent_context._state)
		self._parent_context = parent_context
		self._json_resource = json_resource

	"""def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		super().register_serialized_resource(application_object, json_resource, id)
		if(id and id not in self._json_resource["referenced_resources"]):
			self._json_resource["referenced_resources"].append(id)

	def serialize_buffer(self, data: io.BytesIO) -> str:
		id = super().serialize_buffer(data)
		self._json_resource["referenced_buffers"].append(id)
		return id"""

	def add_task(self, task):
		return self._parent_context.add_task(task)

	def get_root_context(self) -> any:
		return self._parent_context.get_root_context()
