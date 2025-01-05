from typing import Callable
import uuid
import bpy

from ...libstf.stf_processor import STF_Processor
from ...libstf.stf_registry import get_stf_processors


class STF_Component(bpy.types.PropertyGroup):
	"""This property defines the type and ID, from which the appropriate registered function can handle the correct object"""
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name") # type: ignore


class STF_Blender_Component(STF_Processor):
	"""Extension to STF_Processor which also associates a function to draw the component in Blender's UI"""
	blender_property_name: str
	filter: list
	draw_component_func: Callable


class STFAddComponentOperatorBase:
	"""Base class to add an STF component to a Blender object"""
	bl_label = "Add Component"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		target = self.get_property(context)
		component_ref: STF_Component = target.stf_components.add()
		component_ref.stf_id = str(uuid.uuid4())
		component_ref.stf_type = self.stf_type
		component_ref.blender_property_name = self.property_name

		new_component = getattr(target, self.property_name).add()
		new_component.stf_id = component_ref.stf_id
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


class STFDrawComponentList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


def get_component_modules(filter = None) -> list[STF_Blender_Component]:
	ret = []
	for processor in get_stf_processors(bpy.context.preferences.addons.keys()):
		if(isinstance(processor, STF_Blender_Component) or hasattr(processor, "draw_component_func")):
			if(hasattr(processor, "filter") and filter):
				if(filter in getattr(processor, "filter")):
					ret.append(processor)
				else:
					continue
			else:
				ret.append(processor)
	return ret


def get_components_from_object(application_object: any) -> list:
	ret = []
	if(hasattr(application_object, "stf_components")):
		for component_ref in application_object.stf_components:
			components = getattr(application_object, component_ref.blender_property_name)
			for component in components:
				if(component.stf_id == component_ref.stf_id):
					ret.append(component)
	return ret


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component, object: any, component: any):
	box = layout.box()
	box.label(text=component_ref.stf_type)
	box.label(text=component_ref.stf_id)

	modules = get_component_modules()
	selected_module = None
	for module in modules:
		if(module.stf_type == component_ref.stf_type and module.draw_component_func):
			selected_module = module
			break

	if(selected_module):
		selected_module.draw_component_func(box, context, component_ref, object, component)
	else:
		box.label(text="Unknown Type")
		box.label(text="Blender Property Name: " + component_ref.blender_property_name)


def find_component_module(modules: list[STF_Blender_Component], stf_type: str) -> STF_Blender_Component:
	for module in modules:
		if(module.stf_type == stf_type):
			return module


def draw_components_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		object: any,
		add_component_op: str,
		remove_component_op: str
		):
	modules = get_component_modules()

	if(context.scene.stf_component_modules):
		row = layout.row()
		row.prop(bpy.context.scene, "stf_component_modules", text="")
		selected_add_module = find_component_module(modules, context.scene.stf_component_modules)
		if(selected_add_module):
			add_button = row.operator(add_component_op)
			add_button.stf_type = context.scene.stf_component_modules
			add_button.property_name = selected_add_module.blender_property_name

		row = layout.row()
		row.template_list(STFDrawComponentList.bl_idname, "", object, "stf_components", object, "stf_active_component_index")
		if(len(object.stf_components) > object.stf_active_component_index):
			component_ref = object.stf_components[object.stf_active_component_index]

			remove_button = row.operator(remove_component_op, icon="X", text="")
			remove_button.index = object.stf_active_component_index
			remove_button.property_name = component_ref.blender_property_name

			for component in getattr(object, component_ref.blender_property_name):
				if(component.stf_id == component_ref.stf_id):
					draw_component(layout, context, component_ref, object, component)
					break


stf_component_filter = None
def set_stf_component_filter(filter: str = None):
	global stf_component_filter
	stf_component_filter = filter


def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((module.stf_type, module.stf_type, "")) for module in get_component_modules(stf_component_filter)]

def register():
	bpy.types.Scene.stf_component_modules = bpy.props.EnumProperty(
		items=_build_stf_component_types_enum_callback,
		name="STF Component Types",
		description="Default & hot-loaded STF component types",
		options={"SKIP_SAVE"},
		default=0
	)

def unregister():
	if hasattr(bpy.types.Scene, "stf_component_modules"):
		del bpy.types.Scene.stf_component_modules
