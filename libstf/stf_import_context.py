import io

from .stf_report import STFReport
from .stf_file import STF_File
from .stf_processor import STF_Processor


class STF_ImportContext:
	__file: STF_File

	__processors: dict[str, STF_Processor]

	__imported_resources: dict[str, any] # ID -> imported object


	def import_resource(self, json: dict) -> any | None:
		pass

	def import_buffer(self, id: str) -> io.BytesIO:
		pass

	def get_resource(self, id: int) -> dict:
		pass


	def report(self, report: STFReport):
		pass


