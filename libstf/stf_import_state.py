import io
from typing import Callable

from .stf_report import STF_Report_Severity, STFException, STFReport
from .stf_file import STF_File
from .stf_module import STF_ImportHook, STF_Module
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_util import run_tasks


class STF_ImportState:
	"""
	Hold all the data from a file for an import run.
	Each context must have access to the same STF_ImportState instance.
	"""

	def __init__(self, file: STF_File, processors: list[STF_Module]):
		self._file = file

		self._processors: list[STF_Module] = []
		self._hook_processors: list[STF_ImportHook] = []

		for processor in processors:
			if(hasattr(processor, "hook_target_stf_type")):
				self._hook_processors.append(processor)
			else:
				self._processors.append(processor)

		self._imported_resources: dict[str, any] = {} # ID -> imported object
		self._profiles: list[STF_Profile]
		self._asset_info: STF_Meta_AssetInfo
		self._reports: list[STFReport] = []

		self._tasks: list[Callable] = []

	def determine_hooks(self, json_resource: dict) -> list[STF_ImportHook]:
		ret = []
		for processor in self._hook_processors:
			if(json_resource["type"] == processor.hook_target_stf_type):
				ret.append(processor)
		return ret

	def determine_processor(self, json_resource: dict) -> STF_Module:
		for processor in self._processors:
			if(json_resource["type"] == processor.stf_type):
				return processor
		return None

	def register_imported_resource(self, id: str, application_object: any):
		self._imported_resources[id] = application_object

	def import_buffer(self, id: str) -> io.BytesIO:
		buffer = self._file.definition.buffers.get(id)
		match(buffer.type):
			case "stf.buffer.included":
				return self._file.buffers_included[buffer.index]
			case "stf.buffer.file":
				pass # TODO
			case "stf.buffer.json_array":
				pass # TODO
			case _:
				self.report(STFReport("Invalid buffer type: " + buffer.type, severity=STF_Report_Severity.Error))
		return None

	def add_task(self, task: Callable):
		self._tasks.append(task)

	def run_tasks(self):
		run_tasks(self)

	def get_json_resource(self, id: int) -> dict:
		return self._file.definition.resources.get(id)

	def get_root_id(self) -> str:
		return self._file.definition.stf.root

	def report(self, report: STFReport):
		self._reports.append(report)
		if(report.severity == STF_Report_Severity.Error):
			print(report.to_string(), flush=True)
			raise STFException(report)

