import bpy
import json
from typing import Any

from .stf_handler_component import STF_Component_Ref
from .stf_component_resource import add_component
from ...blender_grr import *


__all__ = ["STFAddComponentOperatorBase", "STFRemoveComponentOperatorBase", "STFEditComponentOperatorBase", "ComponentLoadJsonOperatorBase"]


class STFAddComponentOperatorBase:
	"""Base class to add an STF component to a Blender object"""
	bl_label = "Add Component"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore
	default_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context) -> set:
		import uuid
		add_component(self.get_property(context), self.property_name, str(uuid.uuid4()), self.stf_type, self.get_components_ref_property(context), self.default_name)
		return {"FINISHED"}

	def get_property(self, context) -> Any:
		pass

	def get_components_ref_property(self, context) -> Any:
		return self.get_property(context).stf_info.stf_components


class STFRemoveComponentOperatorBase:
	"""Base class to remove an STF component from a Blender object"""
	bl_label = "Remove Component"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context) -> set:
		target = self.get_property(context)
		component_ref = self.get_components_ref_property(context)[self.index]

		if(hasattr(target, self.property_name)):
			component_type_list = getattr(target, self.property_name)
			for target_component_index, component in enumerate(component_type_list):
				if(component.stf_id == component_ref.stf_id):
					component_type_list.remove(target_component_index)
					break
			else:
				self.report({"INFO"}, "No component was referenced")

		self.get_components_ref_property(context).remove(self.index)
		return {"FINISHED"}

	def get_property(self, context) -> Any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_info.stf_components


class STFEditComponentOperatorBase:
	"""Base class to edit a components ID"""
	bl_label = "Edit ID"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	component_id: bpy.props.StringProperty() # type: ignore
	edit_component_id: bpy.props.StringProperty(name="ID") # type: ignore

	def invoke(self, context, event):
		self.edit_component_id = self.component_id
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context) -> set:
		if(not self.edit_component_id):
			self.report({"ERROR"}, "ID can't be empty!")
			return {"CANCELLED"}

		components_refs = self.get_components_ref_property(context)
		for component_ref in components_refs:
			if(component_ref.stf_id == self.component_id):
				if(hasattr(self.get_property(context), component_ref.blender_property_name)):
					components = getattr(self.get_property(context), component_ref.blender_property_name)
					for component in components:
						if(component.stf_id == self.component_id):
							component.stf_id = self.edit_component_id
							component.name = self.edit_component_id
							component_ref.stf_id = self.edit_component_id
							component_ref.name = self.edit_component_id
							return {"FINISHED"}

		self.report({"ERROR"}, "Couldn't change Component ID")
		return {"CANCELLED"}

	def draw(self, context):
		layout: bpy.types.UILayout = self.layout
		layout.prop(self, "edit_component_id")

	def get_property(self, context) -> Any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_info.stf_components


class ComponentLoadJsonOperatorBase():
	bl_label = "Set from Json"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	component_id: bpy.props.StringProperty() # type: ignore

	json_string: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context: bpy.types.Context) -> set:
		try:
			import json
			json_resource = json.loads(self.json_string)

			for component in self.get_property(context):
				if(component.stf_id == self.component_id):
					self.parse_json(context, component, json_resource)
					return {"FINISHED"}
		except Exception as e:
			self.report({"ERROR"}, str(e))
		self.report({"ERROR"}, "Failed applying Json values.")
		return {"CANCELLED"}

	def get_property(self, context: bpy.types.Context) -> Any:
		pass

	def parse_json(self, context: bpy.types.Context, component: Any, json_resource: dict):
		pass

	def draw(self, context: bpy.types.Context):
		layout: bpy.types.UILayout = self.layout
		layout.label(text="Paste json setup string.")
		layout.label(text="(This will overwrite your current values)")

		json_error = False
		try:
			json.loads(self.json_string)
		except Exception:
			json_error = True
		layout.alert = json_error
		layout.prop(self, "json_string", text="", icon="ERROR" if json_error else "NONE")
