import io

from .stf_report import STF_Report_Severity, STFReport
from .stf_file import STF_File
from .stf_module import STF_ImportHook, STF_Module
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_util import StateUtil


class STF_ImportState(StateUtil):
	"""
	Hold all the data from a file for an import run.
	Each context must have access to the same STF_ImportState instance.
	"""

	def __init__(self, file: STF_File, modules: tuple[dict[str, STF_Module], dict[str, list[STF_ImportHook]]]):
		super.__init__()

		self._file = file

		self._modules: dict[str, STF_Module] = modules[0]
		self._hooks: dict[str, list[STF_ImportHook]] = modules[1]

		self._imported_resources: dict[str, any] = {} # ID -> imported object
		self._profiles: list[STF_Profile]
		self._asset_info: STF_Meta_AssetInfo

	def determine_module(self, json_resource: dict) -> STF_Module:
		return self._modules.get(json_resource["type"])

	def determine_hooks(self, json_resource: dict) -> list[STF_ImportHook]:
		return self._hooks.get(json_resource["type"])

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

	def get_json_resource(self, id: int) -> dict:
		return self._file.definition.resources.get(id)

	def get_root_id(self) -> str:
		return self._file.definition.stf.root

