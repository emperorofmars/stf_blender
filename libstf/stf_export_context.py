import io
from typing import Callable

from .stf_export_state import STF_ExportState
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFReport


def run_export_hooks(self, object: any, object_ctx: any):
	for processor in self._state._processors:
		if(hasattr(processor, "target_application_types") and hasattr(processor, "export_hook_func") and type(object) in getattr(processor, "target_application_types")):
			export_hook_func = getattr(processor, "export_hook_func")
			export_hook_func(object_ctx, object)

def export_components(self, object: any, object_ctx: any):
	pass


class STF_RootExportContext:
	_state: STF_ExportState

	_tasks: list[Callable] = []

	def __init__(self, state: STF_ExportState):
		self._state = state

	def get_resource_id(self, application_object: any) -> str | None:
		return self._state.get_resource_id(application_object)

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		self._state.register_serialized_resource(application_object, json_resource, id)

	def serialize_resource(self, application_object: any) -> str | None:
		if(application_object == None): return None
		if(id := self.get_resource_id(application_object)): return id

		if(selected_processor := self._state.determine_processor(application_object)):
			json_resource, id, ctx = selected_processor.export_func(self, application_object)
			if(json_resource and id and ctx):
				self.register_serialized_resource(application_object, json_resource, id)

				# Export components from application native constructs
				run_export_hooks(self, application_object, ctx)

				export_components(self, application_object, ctx)

				return id
			else:
				self.report(STFReport(message="Resource Export Failed", severity=STF_Report_Severity.Error, stf_id=id, stf_type=selected_processor.stf_type, application_object=application_object))
		else:
			self.report(STFReport(message="NO Processor Found", severity=STF_Report_Severity.Error, application_object=application_object))
		return None

	def serialize_buffer(self, data: io.BytesIO) -> str:
		return self._state.serialize_buffer(data)

	def add_task(self, task: Callable):
		self._tasks.append(task)

	def run_tasks(self):
		max_iterations = 1000
		while(len(self._tasks) > 0 and max_iterations > 0):
			taskset = self._tasks
			self._tasks = []
			for task in taskset:
				task()
			max_iterations -= 1
		if(len(self._tasks) > 0):
			self.report(STFReport(message="Recursion", severity=STF_Report_Severity.Error))

	def report(self, report: STFReport):
		# handle severety
		self._state.report(report)

	def get_root_id(self) -> str | None:
		return self._state._root_id

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		return self._state._asset_info

	def get_profiles(self) -> list[STF_Profile]:
		return self._state._profiles

	def get_state(self) -> STF_ExportState:
		return self._state


class STF_ResourceExportContext(STF_RootExportContext):
	_json_resource: dict

	def __init__(self, parent_context: STF_RootExportContext, json_resource: dict):
		super().__init__(parent_context.get_state())
		self._json_resource = json_resource
		self.ensure_resource_properties()

	def ensure_resource_properties(self):
		if(not hasattr(self._json_resource, "referenced_resources")):
			self._json_resource["referenced_resources"] = []
		if(not hasattr(self._json_resource, "referenced_buffers")):
			self._json_resource["referenced_buffers"] = []

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		super().register_serialized_resource(application_object, json_resource, id)
		if(id and id not in self._json_resource["referenced_resources"]):
			self._json_resource["referenced_resources"].append(id)

	def serialize_buffer(self, data: io.BytesIO) -> str:
		id = super().serialize_buffer(data)
		self._json_resource["referenced_buffers"].append(id)
		return id

