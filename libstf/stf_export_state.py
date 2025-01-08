import io
from enum import Enum

from .stf_definition import STF_Buffer_Included, STF_JsonDefinition, STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFReport
from .stf_module import STF_ExportHook, STF_Module
from .stf_file import STF_File
from .stf_util import StateUtil


class STF_Buffer_Mode(Enum):
	included_binary = 0
	included_json = 1
	external = 2


class STF_ExportState(StateUtil):
	"""
	Hold all the data from an export run.
	Each context must have access to the same STF_ExportState instance.
	"""

	def __init__(self, profiles: list[STF_Profile], asset_info: STF_Meta_AssetInfo, modules: tuple[dict[any, STF_Module], dict[any, list[STF_ExportHook]]], fail_on_severity: STF_Report_Severity = STF_Report_Severity.FatalError):
		super().__init__(fail_on_severity)

		self._modules: dict[any, STF_Module] = modules[0]
		self._hooks: dict[any, list[STF_ExportHook]] = modules[1]

		self._resources: dict[any, str] = {} # original application object -> ID of exported STF Json resource
		self._exported_resources: dict[str, dict] = {} # ID -> exported STF Json resource
		self._exported_buffers: dict[str, io.BytesIO] = {} # ID -> exported STF Json buffer

		self._profiles = profiles
		self._asset_info = asset_info
		self._root_id: str = None

	def determine_module(self, application_object: any) -> STF_Module:
		return self._modules.get(type(application_object))

	def determine_hooks(self, application_object: any) -> list[STF_ExportHook]:
		return self._hooks.get(type(application_object), [])

	def get_resource_id(self, application_object: any) -> str:
		if(application_object in self._resources):
			return self._resources[application_object]
		else:
			return None

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		#print("\nRegistering Resource: \n" + id + "\n" + str(application_object) + "\n" + str(json_resource) + "\n", flush=True)
		if(type(id) is not str):
			self.report(STFReport(message="Invalid Resource ID", severity=STF_Report_Severity.Error, stf_id=id, application_object=application_object))
		self._resources[application_object] = id
		self._exported_resources[id] = json_resource

	def serialize_buffer(self, data: io.BytesIO) -> str:
		import uuid
		id = str(uuid.uuid4())
		self._exported_buffers[id] = data
		return id

	def set_root_id(self, id: str):
		self._root_id = id

	def get_root_id(self):
		return self._root_id

	def create_stf_definition(self, buffer_mode: STF_Buffer_Mode = STF_Buffer_Mode.included_binary, generator: str = "libstf_python") -> STF_JsonDefinition:
		import datetime

		ret = STF_JsonDefinition()
		ret.stf.version_major = 0
		ret.stf.version_minor = 0
		ret.stf.root = self._root_id
		ret.stf.generator = generator
		ret.stf.timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
		ret.stf.asset_info = self._asset_info
		ret.stf.profiles = self._profiles
		ret.resources = self._exported_resources
		ret.buffers = {}
		if(buffer_mode == STF_Buffer_Mode.included_binary):
			buffer_index = 0
			for id, buffer in self._exported_buffers.items():
				json_buffer_def = STF_Buffer_Included()
				json_buffer_def.index = buffer_index
				ret.buffers[id] = json_buffer_def
				buffer_index += 1
		# TODO handle other buffer types
		return ret

	def create_stf_binary_file(self, generator: str = "libstf_python") -> STF_File:
		ret = STF_File()
		ret.binary_version_major = 0
		ret.binary_version_minor = 0
		ret.definition = self.create_stf_definition(STF_Buffer_Mode.included_binary, generator)
		for _, buffer in self._exported_buffers.items():
			ret.buffers_included.append(buffer)
		return ret
