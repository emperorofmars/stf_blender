import io
from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STFReport


class STF_RootImportContext:
	"""Context for top level resource import"""

	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._tasks: list[Callable] = []

	def import_resource(self, id: str) -> any:
		if(id in self._state._imported_resources.keys()): return self._state._imported_resources[id]

		json_resource = self.get_json_resource(id)
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

