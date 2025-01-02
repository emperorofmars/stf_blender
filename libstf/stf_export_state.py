import io
from enum import Enum
from typing import Callable

from .stf_definition import STF_JsonDefinition, STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFReport
from .stf_processor import STF_ExportComponentHook, STF_ExportHook, STF_Processor
from .stf_file import STF_File


class STF_Buffer_Mode(Enum):
	included_binary = 0
	included_json = 1
	external = 2


class STF_ExportState:
	"""Hold all the data from an export run. Each context must have access to the same STF_ExportState instance"""
	_processors: list[STF_Processor] = []
	_component_processors: list[STF_ExportComponentHook] = []
	_hook_processors: list[STF_ExportHook] = []

	_root_id: str = None
	_resources: dict[any, str] = {} # original application object -> ID of exported STF Json resource
	_exported_resources: dict[str, dict] = {} # ID -> exported STF Json resource
	_exported_buffers: dict[str, io.BytesIO] = {} # ID -> exported STF Json buffer

	_profiles: list[STF_Profile]
	_asset_info: STF_Meta_AssetInfo

	_reports: list[STFReport] = []

	_get_components_from_resource: Callable[[any], list[any]]

	def __init__(self, profiles: list[STF_Profile], asset_info: STF_Meta_AssetInfo, processors: list[STF_Processor], get_components_from_resource: Callable[[any], list[any]]):
		self._processors = processors
		self._profiles = profiles
		self._asset_info = asset_info
		self._get_components_from_resource = get_components_from_resource
		for processor in processors:
			if(hasattr(processor, "export_component_func")):
				self._component_processors.append(processor)
			if(hasattr(processor, "target_application_types") and hasattr(processor, "export_hook_func")):
				self._hook_processors.append(processor)

	def determine_processor(self, application_object: any) -> STF_Processor:
		for processor in self._processors:
			if(type(application_object) in processor.understood_types):
				return processor
		return None

	def get_components(self, application_object: any) -> list[any]:
		return self._get_components_from_resource(application_object, self._component_processors)

	def get_hook_processors(self, application_object: any) -> list[STF_ExportHook]:
		ret = []
		for hook in self._hook_processors:
			if(type(application_object) in getattr(hook, "target_application_types")):
				ret.append(hook)
		return ret

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


	def create_stf_definition(self, generator: str = "libstf_python") -> STF_JsonDefinition:
		import datetime

		ret = STF_JsonDefinition()
		ret.stf.version_major = 0
		ret.stf.version_minor = 0
		ret.stf.root = self._root_id
		ret.stf.generator = generator
		ret.stf.timestamp = datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat()
		ret.stf.asset_info = self._asset_info
		ret.stf.profiles = self._profiles
		ret.resources = self._exported_resources
		ret.buffers = self._exported_buffers
		return ret


	def create_stf_binary_file(self, generator: str = "libstf_python") -> STF_File:
		ret = STF_File()
		ret.binary_version_major = 0
		ret.binary_version_minor = 0
		ret.definition = self.create_stf_definition(generator)
		return ret
