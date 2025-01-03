import io
from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STFReport
from .stf_util import run_tasks


class STF_ImportContext:
	def __init__(self, state: STF_ImportState):
		self._state: STF_ImportState = state
		self._tasks: list[Callable] = []

	def import_resource(self, id: str) -> any:
		if(id in self._state._imported_resources.keys()): return self._state._imported_resources[id]

		json_resource = self.get_json_resource(id)
		hooks = self._state.determine_hooks(json_resource)
		if(len(hooks) > 0):
			pass
		else:
			processor = self._state.determine_processor(json_resource)
			if(processor):
				return processor.import_func(self, json_resource, id)
			else:
				pass # TODO json fallback
		return None

	def import_buffer(self, id: str) -> io.BytesIO:
		return self._state.import_buffer(id)

	def get_json_resource(self, id: int) -> dict:
		return self._state.get_json_resource(id)

	def get_root_id(self) -> str:
		return self._state._file.definition.stf.root

	def report(self, report: STFReport):
		self._state.report(report)

	def run_tasks(self):
		run_tasks(self)

