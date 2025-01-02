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


def run_export_hooks(self, application_object: any, object_ctx: any):
	for processor in self.__processors:
		if(hasattr(processor, "target_application_types") and hasattr(processor, "export_hook_func") and type(application_object) in getattr(processor, "target_application_types")):
			export_hook_func = getattr(processor, "export_hook_func")
			export_hook_func(object_ctx, application_object)

def export_components(self, application_object: any, object_ctx: any):
	pass


class STF_ExportState:
	_processors: list[STF_Processor]

	_root_id: str = None
	_resources: dict[any, str] = {} # original application object -> ID of exported STF Json resource
	_exported_resources: dict[str, dict] = {} # ID -> exported STF Json resource
	_exported_buffers: dict[str, io.BytesIO] = {} # ID -> exported STF Json buffer

	_profiles: list[STF_Profile]
	_asset_info: STF_Meta_AssetInfo

	_reports: list[STFReport] = []

	def __init__(self, profiles: list[STF_Profile], asset_info: STF_Meta_AssetInfo, processors: list[STF_Processor]):
		self._processors = processors
		self._profiles = profiles
		self._asset_info = asset_info

	def determine_processor(self, application_object: any) -> STF_Processor:
		for processor in self._processors:
			if(type(application_object) in processor.understood_types):
				return processor
		return None

	def get_resource_id(self, application_object: any) -> str:
		if(application_object in self._resources):
			return self._exported_resources[self._resources[application_object]]
		else:
			return None

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		#print("\nRegistering Resource: \n" + id + "\n" + str(application_object) + "\n" + str(json_resource) + "\n")
		self._resources[application_object] = json_resource
		self._exported_resources[id] = json_resource
		if(not self._root_id): # First exported resource is the root
			self._root_id = id

	def serialize_buffer(self, data: io.BytesIO) -> str:
		import uuid
		id = uuid.uuid4()
		self._exported_buffers[id] = data
		return id

	def report(self, report: STFReport):
		# handle severety
		self._reports.append(report)

	def get_root_id(self):
		return self._root_id


def create_stf_definition(context: STF_ExportState, generator: str = "libstf_python") -> STF_JsonDefinition:
	import datetime

	ret = STF_JsonDefinition()
	ret.stf.version_major = 0
	ret.stf.version_minor = 0
	ret.stf.root = context.get_root_id()
	ret.stf.generator = generator
	ret.stf.timestamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
	ret.stf.asset_info = context._asset_info
	ret.stf.profiles = context._profiles
	ret.resources = context._exported_resources
	ret.buffers = context._exported_buffers
	return ret


def create_stf_binary_file(context: STF_ExportState, generator: str = "libstf_python") -> STF_File:
	ret = STF_File()
	ret.binary_version_major = 0
	ret.binary_version_minor = 0
	ret.definition = create_stf_definition(context, generator)
	return ret
