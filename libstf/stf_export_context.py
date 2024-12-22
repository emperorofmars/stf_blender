import io
from enum import Enum

from .stf_definition import STF_Meta
from .stf_report import STFReport
from .stf_processor import STF_Processor
from .stf_file import STF_File


class STF_Buffer_Mode(Enum):
	included_binary = 0
	included_json = 1
	external = 1


class STF_ExportContext:
	__file: STF_File

	__buffer_mode: STF_Buffer_Mode = STF_Buffer_Mode.included_binary
	__processors: dict[str, STF_Processor]

	__resources: dict[any, str] # original object -> ID of exported STF Json resource
	__exported_resources: dict[str, dict] # ID -> exported STF Json resource
	__buffer_definitions: dict[str, dict] # ID -> exported STF Json buffer object

	__meta: STF_Meta


	def serialize_resource(self, object: any) -> dict | None:
		return None

	def serialize_buffer(self, data: io.BytesIO) -> str:
		pass


	def report(self, report: STFReport):
		pass
