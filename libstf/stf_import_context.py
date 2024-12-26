import io

from .stf_report import STFReport
from .stf_file import STF_File
from .stf_processor import STF_Processor


class STF_ImportContext:
	__file: STF_File
	__processors: list[STF_Processor]

	__imported_resources: dict[str, any] # ID -> imported object

	def __init__(self, file: STF_File, processors: list[STF_Processor]):
		self.__file = file
		self.__processors = processors

	def import_resource(self, id: str) -> any:
		pass

	def import_buffer(self, id: str) -> io.BytesIO:
		pass

	def get_json_resource(self, id: int) -> dict:
		pass

	def get_root_id(self) -> str:
		return self.__file.definition.stf.root


	def report(self, report: STFReport):
		pass

