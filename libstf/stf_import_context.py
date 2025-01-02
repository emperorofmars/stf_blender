import io
from typing import Callable

from .stf_import_state import STF_ImportState
from .stf_report import STFReport
from .stf_util import run_tasks


class STF_ImportContext:
	_state: STF_ImportState

	_tasks: list[Callable] = []

	def __init__(self, state: STF_ImportState):
		self._state = state

	def import_resource(self, id: str) -> any:
		pass

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

