import io
from typing import Callable


from .stf_export_state import STF_ExportState
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFReport
from .stf_util import run_tasks


class STF_RootExportContext:
	"""Context for top level resource export"""

	def __init__(self, state: STF_ExportState):
		self._state = state
		self._tasks: list[Callable] = []

	def get_resource_id(self, application_object: any) -> str | None:
		return self._state.get_resource_id(application_object)

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		self._state.register_serialized_resource(application_object, json_resource, id)

	def serialize_resource(self, application_object: any) -> str | None:
		if(application_object == None): return None
		if(id := self.get_resource_id(application_object)): return id

		if(selected_processor := self._state.determine_processor(application_object)):
			json_resource, id, ctx = selected_processor.export_func(self, application_object, None)

			if(json_resource and id and ctx):
				self.register_serialized_resource(application_object, json_resource, id)

				# Export components from application native constructs
				for processor in self._state.determine_hooks(application_object):
					processor.export_func(ctx, application_object, None)

				# Export components explicitely defined by this application
				if(hasattr(selected_processor, "get_components_func")):
					components = selected_processor.get_components_func(self, application_object)
					if(len(components) > 0):
						if(not hasattr(json_resource, "components")):
							json_resource["components"] = {}
						for component in components:
							if(selected_processor := self._state.determine_processor(component)):
								component_json_resource, component_id, _ = selected_processor.export_func(ctx, component, application_object)
								json_resource["components"][component_id] = component_json_resource
							# TODO else warn user about unsupported component

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
		run_tasks(self)

	def report(self, report: STFReport):
		self._state.report(report)

	def get_root_id(self) -> str | None:
		return self._state._root_id

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		return self._state._asset_info

	def get_profiles(self) -> list[STF_Profile]:
		return self._state._profiles


class STF_ResourceExportContext(STF_RootExportContext):
	"""
		Context for the export of sub-resources.

		Extend this class if you need a custom context for sub-resources.
	"""

	def __init__(self, parent_context: STF_RootExportContext, json_resource: dict):
		super().__init__(parent_context._state)
		self._parent_context = parent_context
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

	def add_task(self, task):
		return self._parent_context.add_task(task)

