from .stf_report import STFReportSeverity, STFReport
from .stf_file import STF_File
from .stf_module import STF_Module
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_util import StateUtil


class STF_ImportState(StateUtil):
	"""
	Hold all the data from a file for an import run.
	Each context must have access to the same STF_ImportState instance.
	"""

	def __init__(self, file: STF_File, modules: dict[str, STF_Module], fail_on_severity: STFReportSeverity = STFReportSeverity.FatalError):
		super().__init__(fail_on_severity)

		self._file = file

		self._modules: dict[str, STF_Module] = modules

		self._imported_resources: dict[str, any] = {} # ID | list of IDs -> imported object
		self._profiles: list[STF_Profile]
		self._asset_info: STF_Meta_AssetInfo


	def determine_module(self, json_resource: dict) -> STF_Module:
		return self._modules.get(json_resource["type"])

	def register_imported_resource(self, stf_id: str, application_object: any):
		self._imported_resources[stf_id] = application_object

	def get_imported_resource(self, stf_id: str):
		return self._imported_resources.get(stf_id, None)

	def import_buffer(self, stf_id: str) -> bytes:
		buffer = self._file.definition.buffers.get(stf_id)
		match(buffer.type):
			case "stf.buffer.included":
				return self._file.buffers_included[buffer.index]
			case "stf.buffer.file":
				pass # TODO
			case "stf.buffer.json_array":
				pass # TODO
			case _:
				self.report(STFReport("Invalid buffer type: " + buffer.type, severity=STFReportSeverity.Error))
		return None

	def get_json_resource(self, stf_id: int) -> dict:
		return self._file.definition.resources.get(stf_id)

	def get_root_id(self) -> str:
		return self._file.definition.stf.root

