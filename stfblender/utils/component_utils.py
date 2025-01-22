from typing import Callable
import uuid
import bpy

from ...libstf.stf_module import STF_Module


class STF_BlenderComponentModule(STF_Module):
	"""Extension to STF_Module which also associates a function to draw the component in Blender's UI"""
	blender_property_name: str
	filter: list
	draw_component_func: Callable


class STF_BlenderComponentBase(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="Name") # type: ignore


class STF_Component(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""This property defines the type and ID, from which the appropriate registered function can handle the correct object"""
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name") # type: ignore


def add_component(application_object: any, blender_property_name: str, stf_id: str, stf_type: str) -> tuple[STF_Component, any]:
	component_ref: STF_Component = application_object.stf_components.add()
	component_ref.stf_id = stf_id
	component_ref.stf_type = stf_type
	component_ref.blender_property_name = blender_property_name

	new_component = getattr(application_object, blender_property_name).add()
	new_component.stf_id = component_ref.stf_id

	return (component_ref, new_component)

class STFAddComponentOperatorBase:
	"""Base class to add an STF component to a Blender object"""
	bl_label = "Add Component"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		add_component(self.get_property(context), self.property_name, str(uuid.uuid4()), self.stf_type)
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


class STFRemoveComponentOperatorBase:
	"""Base class to remove an STF component from a Blender object"""
	bl_label = "Remove Component"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		target = self.get_property(context)
		component_ref = target.stf_components[self.index]

		component_type_list = getattr(target, self.property_name)
		target_component_index = None
		for index, component in enumerate(component_type_list):
			if(component.stf_id == component_ref.stf_id):
				target_component_index = index
				break

		component_type_list.remove(target_component_index)
		target.stf_components.remove(self.index)
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


def get_components_from_object(application_object: any) -> list:
	ret = []
	if(hasattr(application_object, "stf_components")):
		for component_ref in application_object.stf_components:
			components = getattr(application_object, component_ref.blender_property_name)
			for component in components:
				if(component.stf_id == component_ref.stf_id):
					ret.append(component)
	return ret
