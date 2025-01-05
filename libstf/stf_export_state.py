import io
from enum import Enum
from typing import Callable

from .stf_definition import STF_JsonDefinition, STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFException, STFReport
from .stf_processor import STF_ExportHook, STF_Processor
from .stf_file import STF_File
from .stf_util import run_tasks


class STF_Buffer_Mode(Enum):
	included_binary = 0
	included_json = 1
	external = 2


class STF_ExportState:
	"""
	Hold all the data from an export run.
	Each context must have access to the same STF_ExportState instance.
	"""

	def __init__(self, profiles: list[STF_Profile], asset_info: STF_Meta_AssetInfo, processors: list[STF_Processor]):
		self._processors: list[STF_Processor] = []
		self._hook_processors: list[STF_ExportHook] = []

		for processor in processors:
			if(hasattr(processor, "hook_target_application_types")): #and hasattr(processor, "export_hook_func")
				self._hook_processors.append(processor)
			else:
				self._processors.append(processor)

		self._resources: dict[any, str] = {} # original application object -> ID of exported STF Json resource
		self._exported_resources: dict[str, dict] = {} # ID -> exported STF Json resource
		self._exported_buffers: dict[str, io.BytesIO] = {} # ID -> exported STF Json buffer

		self._profiles = profiles
		self._asset_info = asset_info
		self._reports: list[STFReport] = []
		self._root_id: str = None

		self._tasks: list[Callable] = []

	def determine_processor(self, application_object: any) -> STF_Processor:
		for processor in self._processors:
			if(type(application_object) in processor.understood_application_types):
				return processor
		return None

	def determine_hooks(self, application_object: any) -> list[STF_ExportHook]:
		ret = []
		for hook in self._hook_processors:
			if(type(application_object) in hook.hook_target_application_types):
				ret.append(hook)
		return ret

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
		if(not self._root_id): # First exported resource is the root
			self._root_id = id

	def serialize_buffer(self, data: io.BytesIO) -> str:
		import uuid
		id = uuid.uuid4()
		self._exported_buffers[id] = data
		return id

	def add_task(self, task: Callable):
		self._tasks.append(task)

	def run_tasks(self):
		run_tasks(self)

	def report(self, report: STFReport):
		self._reports.append(report)
		if(report.severity == STF_Report_Severity.Error):
			print(report.to_string(), flush=True)
			raise STFException(report)

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
