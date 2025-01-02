import io

from .stf_report import STFReport
from .stf_file import STF_File
from .stf_processor import STF_Processor
from .stf_definition import STF_Meta_AssetInfo, STF_Profile


class STF_ImportState:
	_file: STF_File
	_processors: list[STF_Processor]

	_imported_resources: dict[str, any] # ID -> imported object

	_profiles: list[STF_Profile]
	_asset_info: STF_Meta_AssetInfo

	_reports: list[STFReport] = []

	def __init__(self, file: STF_File, processors: list[STF_Processor]):
		self._file = file
		self._processors = processors

	def determine_processor(self, json_resource: dict) -> STF_Processor:
		pass

	def import_buffer(self, id: str) -> io.BytesIO:
		pass

	def get_json_resource(self, id: int) -> dict:
		pass

	def get_root_id(self) -> str:
		return self._file.definition.stf.root


	def report(self, report: STFReport):
		# handle severety
		self._reports.append(report)

