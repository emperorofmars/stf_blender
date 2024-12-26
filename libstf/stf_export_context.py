import io
from enum import Enum

from .stf_definition import STF_JsonDefinition, STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFReport
from .stf_processor import STF_Processor
from .stf_file import STF_File


class STF_Buffer_Mode(Enum):
	included_binary = 0
	included_json = 1
	external = 1


class STF_ExportContext:
	__processors: list[STF_Processor]

	__root_id: str = None
	__resources: dict[any, str] = {} # original object -> ID of exported STF Json resource
	__exported_resources: dict[str, dict] = {} # ID -> exported STF Json resource
	__exported_buffers: dict[str, io.BytesIO] = {} # ID -> exported STF Json buffer

	__profiles: list[STF_Profile]
	__asset_info: STF_Meta_AssetInfo

	__reports: list[STFReport] = []

	def __init__(self, profiles: list[STF_Profile], asset_info: STF_Meta_AssetInfo, processors: list[STF_Processor]):
		self.__processors = processors
		self.__profiles = profiles
		self.__asset_info = asset_info

	def serialize_resource(self, object: any) -> str | None:
		if(object in self.__resources):
			return self.__exported_resources[self.__resources[object]]

		selected_processor = None
		for processor in self.__processors:
			if(type(object) in processor.understood_types):
				selected_processor = processor
				break

		if(selected_processor):
			print(selected_processor)
			resource, id = selected_processor.export_func(self, object)
			if(resource and id):
				self.__resources[object] = resource
				self.__exported_resources[id] = resource
				if(not self.__root_id):
					self.__root_id = id
				return id
			else:
				self.report(STFReport(message="Resource Export Failed", stf_severity=STF_Report_Severity.Error, stf_id=id, stf_type=selected_processor.stf_type, application_object=object))
		else:
			self.report(STFReport(message="NO Processor Found!", stf_severity=STF_Report_Severity.Error, application_object=object))
		return None

	def serialize_buffer(self, data: io.BytesIO) -> str:
		import uuid

		id = uuid.uuid4()
		self.__exported_buffers[id] = data


	def report(self, report: STFReport):
		# handle severety
		self.__reports.append(report)


	def get_root_id(self) -> str | None:
		return self.__root_id

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		return self.__asset_info

	def get_profiles(self) -> list[STF_Profile]:
		return self.__profiles

	def get_exported_resources(self) -> dict[str, dict]:
		return self.__exported_resources

	def get_exported_buffers(self) -> dict[str, io.BytesIO]:
		return self.__exported_buffers


class STF_DataExportContext:
	__context: STF_ExportContext
	__resource: dict
	def __init__(self, context: STF_ExportContext, resource: dict):
		self.__context = context

	def serialize_resource(self, resource: object) -> int:
		#self.__resource["referenced_resources"][index]
		pass


def create_stf_definition(context: STF_ExportContext, generator: str = "libstf_python") -> STF_JsonDefinition:
	import datetime

	ret = STF_JsonDefinition()
	ret.stf.version_major = 0
	ret.stf.version_minor = 0
	ret.stf.root = context.get_root_id()
	ret.stf.generator = generator
	ret.stf.timestamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
	ret.stf.asset_info = context.get_asset_info()
	ret.stf.profiles = context.get_profiles()
	ret.resources = context.get_exported_resources()
	ret.buffers = context.get_exported_buffers()
	return ret


def create_stf_binary_file(context: STF_ExportContext, generator: str = "libstf_python") -> STF_File:
	ret = STF_File()
	ret.binary_version_major = 0
	ret.binary_version_minor = 0
	ret.definition = create_stf_definition(context, generator)
	return ret
