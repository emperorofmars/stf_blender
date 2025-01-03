import io

from .stf_report import STF_Report_Severity, STFException, STFReport
from .stf_file import STF_File
from .stf_processor import STF_ImportHook, STF_Processor
from .stf_definition import STF_Meta_AssetInfo, STF_Profile


class STF_ImportState:

	def __init__(self, file: STF_File, processors: list[STF_Processor]):
		self._file = file

		self._processors: list[STF_Processor] = []
		self._hook_processors: list[STF_ImportHook] = []

		for processor in processors:
			if(hasattr(processor, "import_func")):
				self._processors.append(processor)
			if(hasattr(processor, "import_resource_func") and hasattr(processor, "target_stf_type")):
				self._hook_processors.append(processor)

		self._imported_resources: dict[str, any] = {} # ID -> imported object
		self._profiles: list[STF_Profile]
		self._asset_info: STF_Meta_AssetInfo
		self._reports: list[STFReport] = []

	def determine_hooks(self, json_resource: dict) -> list[STF_ImportHook]:
		ret = []
		for processor in self._hook_processors:
			if(json_resource["type"] == processor.target_stf_type):
				ret.append(processor)
		return ret

	def determine_processor(self, json_resource: dict) -> STF_Processor:
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
				pass
			case "stf.buffer.json_array":
				pass
			case _:
				self.report(STFReport("Invalid buffer type: " + buffer.type))
		return None

	def get_json_resource(self, id: int) -> dict:
		return self._file.definition.resources.get(id)

	def get_root_id(self) -> str:
		return self._file.definition.stf.root

	def report(self, report: STFReport):
		self._reports.append(report)
		if(report.severity == STF_Report_Severity.Error):
			print(report.to_string(), flush=True)
			raise STFException(report)

