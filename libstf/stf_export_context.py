import io
from typing import Callable

from .stf_export_state import STF_ExportState
from .stf_definition import STF_Meta_AssetInfo, STF_Profile
from .stf_report import STFReportSeverity, STFReport


class STF_ExportContext:
	"""Context for top level resource export. An instance of this will be passed to each STF_Module's export func."""

	def __init__(self, state: STF_ExportState):
		self._state = state


	def get_resource_id(self, application_object: any) -> str | None:
		return self._state.get_resource_id(application_object)

	def register_id(self, application_object: any, stf_id: str):
		self._state.register_id(application_object, stf_id)

	def register_serialized_resource(self, application_object: any, json_resource: dict, stf_id: str):
		self._state.register_serialized_resource(application_object, json_resource, stf_id)


	def __run_hooks(self, application_object: any, json_resource: dict, stf_id: str):
		"""Export components from application native constructs"""
		if(hooks := self._state.determine_hooks(application_object)):
			for hook in hooks:
				can_handle, hook_objects = hook.hook_can_handle_application_object_func(application_object)
				if(can_handle and hook_objects and len(hook_objects) > 0):
					if("components" not in json_resource): json_resource["components"] = []
					for hook_object in hook_objects:
						hook_ret = hook.export_func(self, hook_object, application_object)
						if(hook_ret):
							hook_json_resource, hook_id = hook_ret
							self._state.register_serialized_resource(hook_object, hook_json_resource, hook_id)
							json_resource["components"].append(hook_id)
						else:
							self.report(STFReport("Export Hook Failed", STFReportSeverity.Error, stf_id, hook.stf_type, application_object))


	def __run_components(self, application_object: any, json_resource: dict, stf_id: str, components: list):
		"""Export components explicitely defined by this application"""
		if(len(components) > 0):
			if("components" not in json_resource): json_resource["components"] = []
			for component in components:
				if(selected_module := self._state.determine_module(component, "component")):
					component_ret = selected_module.export_func(self, component, application_object)
					if(component_ret):
						component_json_resource, component_id = component_ret
						self._state.register_serialized_resource(component, component_json_resource, component_id)
						json_resource["components"].append(component_id)
					else:
						self.report(STFReport("Export Component Failed", STFReportSeverity.Error, stf_id, selected_module.stf_type, application_object))
				else:
					self.report(STFReport("Unsupported Component", STFReportSeverity.Warn, None, None, application_object))


	def serialize_resource(self, application_object: any, context_object: any = None, module_kind = None) -> str | None:
		"""Run all logic to serialize an application resource. If it already has been serialized, return the existing ID."""

		if(application_object == None): return None
		if(existing_id := self.get_resource_id(application_object)): return existing_id

		if(selected_module := self._state.determine_module(application_object, module_kind)):
			module_ret = selected_module.export_func(self, application_object, context_object)

			if(module_ret):
				json_resource, resource_id = module_ret
				self._state.register_serialized_resource(application_object, json_resource, resource_id)

				if(selected_module.stf_kind not in ["component", "instance"]):
					# Export components from application native constructs
					self.__run_hooks(application_object, json_resource, resource_id)

					if(hasattr(selected_module, "get_components_func")):
						# Export components explicitely defined
						components = selected_module.get_components_func(application_object)
						self.__run_components(application_object, json_resource, resource_id, components)

				return resource_id
			else:
				self.report(STFReport("Resource Export Failed", STFReportSeverity.Error, None, selected_module.stf_type, application_object))
		else:
			self.report(STFReport("NO Module Found", STFReportSeverity.Error, None, None, application_object))
		return None


	def serialize_buffer(self, data: bytes) -> str:
		return self._state.serialize_buffer(data)


	def translate_application_property(self, application_object: any, application_property: str, property_index: int) -> any:
		if(application_object == None): return None

		selected_module = self._state.determine_module(application_object)
		if(selected_module and hasattr(selected_module, "translate_property_to_stf_func")):
			return selected_module.translate_property_to_stf_func(application_object, application_property, property_index)

		selected_hooks = self._state.determine_hooks(application_object)
		for hook in selected_hooks:
			if(hook and hasattr(hook, "translate_property_to_stf_func")):
				return hook.translate_property_to_stf_func(application_object, application_property, property_index)

		if(hasattr(selected_module, "get_components_func")):
			components = selected_module.get_components_func(application_object)
			for component in components:
				if(component and hasattr(component, "translate_property_to_stf_func")):
					return component.translate_property_to_stf_func(application_object, application_property, property_index)

		return None


	def add_task(self, task: Callable):
		"""Add a task which will be execuded after everything else."""
		self._state._tasks.append(task)


	def report(self, report: STFReport):
		self._state.report(report)


	def id_exists(self, stf_id: str) -> bool:
		return self._state.id_exists(stf_id)


	def get_root_id(self) -> str | None:
		return self._state._root_id

	def get_asset_info(self) -> STF_Meta_AssetInfo:
		return self._state._asset_info

	def get_profiles(self) -> list[STF_Profile]:
		return self._state._profiles

"""
	def ensure_resource_properties(self):
		if(not hasattr(self._json_resource, "referenced_resources")):
			self._json_resource["referenced_resources"] = []
		if(not hasattr(self._json_resource, "referenced_buffers")):
			self._json_resource["referenced_buffers"] = []

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		#self._parent_context.register_serialized_resource(application_object, json_resource, id)
		super().register_serialized_resource(application_object, json_resource, id)
		if(id and id not in self._json_resource["referenced_resources"]):
			self._json_resource["referenced_resources"].append(id)

	def serialize_buffer(self, data: bytes) -> str:
		#id = self._parent_context.serialize_buffer(data)
		id = super().serialize_buffer(data)
		self._json_resource["referenced_buffers"].append(id)
		return id
"""
