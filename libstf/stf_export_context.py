import io
from typing import Callable

from .stf_export_state import STF_ExportState
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_report import STF_Report_Severity, STFReport


class STF_RootExportContext:
	"""Context for top level resource export"""

	def __init__(self, state: STF_ExportState):
		self._state = state


	def get_resource_id(self, application_object: any) -> str | None:
		return self._state.get_resource_id(application_object)

	def get_parent_application_object(self) -> any:
		return None

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		self._state.register_serialized_resource(application_object, json_resource, id)


	def run_hooks(self, application_object: any, object_ctx: any, json_resource: dict, id: str):
		# Export components from application native constructs
		if(hooks := self._state.determine_hooks(application_object)):
			for hook in hooks:
				can_handle, hook_object = hook.hook_can_handle_application_object_func(application_object)
				if(can_handle):
					hook_ret = hook.export_func(object_ctx, hook_object, application_object)
					if(hook_ret):
						hook_json_resource, hook_id, hook_ctx = hook_ret
						if(hook.stf_kind == "component"):
							if("components" not in json_resource): json_resource["components"] = {}
							json_resource["components"][hook_id] = hook_json_resource
						else:
							self.register_serialized_resource(hook_json_resource, hook_id, hook_ctx)
					else:
						self.report(STFReport("Export Hook Failed", STF_Report_Severity.Error, id, hook.stf_type, application_object))


	def run_components(self, application_object: any, object_ctx: any, json_resource: dict, id: str, components: list):
		# Export components explicitely defined by this application
		if(len(components) > 0):
			if("components" not in json_resource): json_resource["components"] = {}
			for component in components:
				if(selected_module := self._state.determine_module(component)):
					component_ret = selected_module.export_func(object_ctx, component, application_object)
					if(component_ret):
						component_json_resource, component_id, _ = component_ret
						json_resource["components"][component_id] = component_json_resource
					else:
						self.report(STFReport("Export Component Failed", STF_Report_Severity.Error, id, selected_module.stf_type, application_object))
				else:
					self.report(STFReport("Unsupported Component", STF_Report_Severity.Warn, None, None, application_object))


	def serialize_resource(self, application_object: any, parent_application_object: any = None) -> str | None:
		if(application_object == None): return None
		if(id := self.get_resource_id(application_object)): return id

		if(selected_module := self._state.determine_module(application_object)):
			module_ret = selected_module.export_func(self.get_root_context() if selected_module.stf_kind == "data" else self, application_object, parent_application_object if parent_application_object else self.get_parent_application_object())
			if(module_ret):
				json_resource, id, ctx = module_ret
				self.register_serialized_resource(application_object, json_resource, id)

				# Export components from application native constructs
				self.run_hooks(application_object, ctx, json_resource, id)

				# Export components explicitely defined by this application
				if(selected_module.stf_kind != "component" and hasattr(selected_module, "get_components_func")):
					components = selected_module.get_components_func(application_object)
					self.run_components(application_object, ctx, json_resource, id, components)

				return id
			else:
				self.report(STFReport("Resource Export Failed", STF_Report_Severity.Error, None, selected_module.stf_type, application_object))
		else:
			self.report(STFReport("NO Processor Found", STF_Report_Severity.Error, None, None, application_object))
		return None


	def serialize_buffer(self, data: io.BytesIO) -> str:
		return self._state.serialize_buffer(data)

	def add_task(self, task: Callable):
		self._state._tasks.append(task)

	def get_root_context(self) -> any:
		return self

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

	def __init__(self, parent_context: STF_RootExportContext, json_resource: dict, parent_application_object: any):
		super().__init__(parent_context._state)
		self._parent_context = parent_context
		self._json_resource = json_resource
		self._parent_application_object = parent_application_object
		self.ensure_resource_properties()

	def get_parent_application_object(self) -> any:
		return self._parent_application_object

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

	def get_root_context(self) -> any:
		return self._parent_context.get_root_context()

