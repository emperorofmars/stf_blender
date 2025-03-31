import io
from enum import Enum

from .stf_definition import STF_Buffer_Included, STF_JsonDefinition, STF_Meta_AssetInfo, STF_Profile
from .stf_report import STFReportSeverity, STFReport
from .stf_module import STF_ExportComponentHook, STF_Module
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

	def __init__(self, profiles: list[STF_Profile], asset_info: STF_Meta_AssetInfo, modules: tuple[dict[any, list[STF_Module]], dict[any, list[STF_ExportComponentHook]]], fail_on_severity: STFReportSeverity = STFReportSeverity.FatalError, permit_id_reassignment: bool = True, metric_multiplier: float = 1):
		super().__init__(fail_on_severity)

		self._modules: dict[any, list[STF_Module]] = modules[0]
		self._hooks: dict[any, list[STF_ExportComponentHook]] = modules[1]

		self._resources: dict[any, str] = {} # original application object -> ID of exported STF Json resource
		self._exported_resources: dict[str, dict] = {} # ID -> exported STF Json resource
		self._exported_buffers: dict[str, io.BytesIO] = {} # ID -> exported STF Json buffer

		self._profiles = profiles
		self._asset_info = asset_info
		self._permit_id_reassignment = permit_id_reassignment
		self._root_id: str = None
		self._metric_multiplier = metric_multiplier


	def determine_module(self, application_object: any, module_kind: str = None) -> STF_Module:
		"""Find the best suited registered STF_Module for the type of this object"""
		selected_module = None
		selected_priority = -1

		for module in self._modules.get(type(application_object), []):
			if(hasattr(module, "can_handle_application_object_func")):
				prio = module.can_handle_application_object_func(application_object)
				if(prio > selected_priority and (module_kind == None or module.stf_kind == module_kind)):
					selected_module = module
					selected_priority = prio
			elif(1 > selected_priority):
				selected_module = module
				selected_priority = 1
		return selected_module


	def determine_hooks(self, application_object: any) -> list[STF_ExportComponentHook]:
		return self._hooks.get(type(application_object), [])


	def determine_property_resolution_module(self, application_object: any, data_path: str) -> STF_Module:
		# TODO handle priority for animation path handling maybe at some point?

		for module in self._modules.get(type(application_object), []):
			if(hasattr(module, "understood_application_property_path_types") and type(application_object) in module.understood_application_property_path_types
					and hasattr(module, "understood_application_property_path_parts")
					and hasattr(module, "resolve_property_path_to_stf_func")):
				for understood_property in module.understood_application_property_path_parts:
					if(data_path.startswith(understood_property)):
						return module

		return None


	def get_resource_id(self, application_object: any) -> str:
		"""Get the ID this object will be referenced by. The object may not be fully serialized yet."""
		if(application_object in self._resources):
			return self._resources[application_object]
		else:
			return None


	def register_id(self, application_object: any, id: str):
		"""Register the ID for this object. The object has not been serialized yet."""
		self._resources[application_object] = id


	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		"""Now register the fully serialized object."""
		if(type(id) is not str):
			self.report(STFReport("Invalid Resource ID", STFReportSeverity.Error, id, json_resource.get("type"), application_object))
		if(id in self._exported_resources):
			self.report(STFReport("Duplicate Resource ID", STFReportSeverity.FatalError, id, json_resource.get("type"), application_object))
			return
		if("referenced_resources" in json_resource and id in json_resource["referenced_resources"]):
			self.report(STFReport("Resource recursion detected!", STFReportSeverity.FatalError, id, json_resource.get("type"), application_object))
			return
		# TODO check for resource loops

		self._exported_resources[id] = json_resource


	def serialize_buffer(self, data: bytes) -> str:
		"""Register a serialized buffer."""
		import uuid
		id = str(uuid.uuid4())
		self._exported_buffers[id] = data
		return id


	def id_exists(self, id: str) -> bool:
		return id in self._resources

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
		ret.stf.metric_multiplier = self._metric_multiplier
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
