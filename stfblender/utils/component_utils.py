import json
from typing import Callable
import uuid
import bpy

from ..core.stf_module import STF_Module
from ..core.stf_registry import get_stf_modules


class STF_Component_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""This property defines the type and ID, from which the appropriate registered function can find the correct component in the `blender_property_name` property of the appropriate Blender construct."""
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name") # type: ignore

class STF_BlenderComponentModule(STF_Module):
	"""Extension to STF_Module which also associates a function to draw the component in Blender's UI"""
	blender_property_name: str
	filter: list
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentModule) -> None
	draw_component_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, any, any], None]


class InstanceModComponentRef(STF_Component_Ref):
	"""Used by armature instances to add or modify a component on an instance of a bone"""
	bone: bpy.props.StringProperty(name="Bone") # type: ignore
	override: bpy.props.BoolProperty(name="Enable Instance Override", default=False) # type: ignore

class STF_BlenderBoneComponentModule(STF_BlenderComponentModule):
	"""Use for components that are allowed on bones and are animatable or can have different values per instance of the armature."""
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentModule) -> None
	draw_component_instance_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, any, any], None]
	# (context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentModule, standin_component: STF_BlenderComponentModule) -> None
	set_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, any, any, any], None]

	# (context: bpy.types.Context, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentModule, context_object: any) -> json_resource: dict
	serialize_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, STF_BlenderComponentModule, any], dict]
	# (context: bpy.types.Context, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentModule, context_object: any) -> None
	parse_component_instance_standin_func: Callable[[bpy.types.Context, dict, STF_Component_Ref, STF_BlenderComponentModule, any], None]


class STF_BlenderComponentOverride(bpy.types.PropertyGroup):
	target_id: bpy.props.StringProperty(name="ID") # type: ignore

class STF_BlenderComponentBase(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="Name") # type: ignore
	overrides: bpy.props.CollectionProperty(type=STF_BlenderComponentOverride, name="Overrides") # type: ignore
	enabled: bpy.props.BoolProperty(name="Enabled", default=True) # type: ignore


def get_component_modules(filter = None) -> list[STF_BlenderComponentModule]:
	ret = []
	for stf_module in get_stf_modules(bpy.context.preferences.addons.keys()):
		if(isinstance(stf_module, STF_BlenderComponentModule) or hasattr(stf_module, "blender_property_name") and hasattr(stf_module, "filter")):
			if(hasattr(stf_module, "filter") and filter):
				if(filter in getattr(stf_module, "filter")):
					ret.append(stf_module)
				else:
					continue
			else:
				ret.append(stf_module)
	return ret


def find_component_module(stf_modules: list[STF_BlenderComponentModule], stf_type: str) -> STF_BlenderComponentModule:
	for stf_module in stf_modules:
		if(stf_module.stf_type == stf_type):
			return stf_module


def add_component(application_object: any, blender_property_name: str, stf_id: str, stf_type: str, components_ref_property: any = None) -> tuple[STF_Component_Ref, any]:
	if(components_ref_property is None):
		components_ref_property = application_object.stf_components
	component_ref: STF_Component_Ref = components_ref_property.add()
	component_ref.stf_id = stf_id
	component_ref.stf_type = stf_type
	component_ref.blender_property_name = blender_property_name

	new_component = getattr(application_object, blender_property_name).add()
	new_component.stf_id = component_ref.stf_id

	return (component_ref, new_component)

class STFAddComponentOperatorBase:
	"""Base class to add an STF component to a Blender object"""
	bl_label = "Add Component"
	bl_options = {"REGISTER", "UNDO"}

	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		add_component(self.get_property(context), self.property_name, str(uuid.uuid4()), self.stf_type, self.get_components_ref_property(context))
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_components


class STFRemoveComponentOperatorBase:
	"""Base class to remove an STF component from a Blender object"""
	bl_label = "Remove Component"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		target = self.get_property(context)
		component_ref = self.get_components_ref_property(context)[self.index]

		if(hasattr(target, self.property_name)):
			component_type_list = getattr(target, self.property_name)
			target_component_index = None
			for index, component in enumerate(component_type_list):
				if(component.stf_id == component_ref.stf_id):
					target_component_index = index
					break
			component_type_list.remove(target_component_index)

		self.get_components_ref_property(context).remove(self.index)
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_components


class STFEditComponentOperatorBase:
	"""Base class to edit a components ID"""
	bl_label = "Edit ID"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore
	edit_component_id: bpy.props.StringProperty(name="ID") # type: ignore

	def invoke(self, context, event):
		self.edit_component_id = self.component_id

		context.scene.workaround_for_blenders_datamodel__component_overrides.clear()
		
		found_overrides = False
		components_refs = self.get_components_ref_property(context)
		for component_ref in components_refs:
			if(component_ref.stf_id == self.component_id):
				if(hasattr(self.get_property(context), component_ref.blender_property_name)):
					components = getattr(self.get_property(context), component_ref.blender_property_name)
					for component in components:
						if(component.stf_id == self.component_id):
							for override in component.overrides:
								added = context.scene.workaround_for_blenders_datamodel__component_overrides.add()
								added.target_id = override.target_id
							found_overrides = True
							break
					if(found_overrides): break
			if(found_overrides): break

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		components_refs = self.get_components_ref_property(context)
		for component_ref in components_refs:
			if(component_ref.stf_id == self.component_id):
				if(hasattr(self.get_property(context), component_ref.blender_property_name)):
					components = getattr(self.get_property(context), component_ref.blender_property_name)
					for component in components:
						if(component.stf_id == self.component_id):
							component.stf_id = self.edit_component_id
							component_ref.stf_id = self.edit_component_id
							component.overrides.clear()
							for override in context.scene.workaround_for_blenders_datamodel__component_overrides:
								if(override.target_id):
									component.overrides.add().target_id = override.target_id
							return {"FINISHED"}

		self.report({"ERROR"}, "Couldn't change Component ID")
		return {"CANCELLED"}

	def draw(self, context):
		layout: bpy.types.UILayout = self.layout
		self.layout.prop(self, "edit_component_id")

		self.layout.prop(context.scene, "workaround_for_blenders_datamodel__component_overrides")
		for index, override in enumerate(context.scene.workaround_for_blenders_datamodel__component_overrides):
			row = self.layout.row()
			row.prop(override, "target_id")
			row.operator(RemoveOverrideFromComponent.bl_idname, text="", icon="X").index = index
		self.layout.operator(AddOverrideToComponent.bl_idname)

	def get_property(self, context) -> any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_components


class AddOverrideToComponent(bpy.types.Operator):
	"""Add override to component"""
	bl_idname = "stf.add_override_to_component"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		bpy.context.scene.workaround_for_blenders_datamodel__component_overrides.add()
		return {"FINISHED"}

class RemoveOverrideFromComponent(bpy.types.Operator):
	"""Add override to component"""
	bl_idname = "stf.remove_override_from_component"
	bl_label = "Remove"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(default=-1) # type: ignore

	def execute(self, context):
		bpy.context.scene.workaround_for_blenders_datamodel__component_overrides.remove(self.index)
		return {"FINISHED"}


def get_components_from_object(application_object: any) -> list:
	ret = []
	if(hasattr(application_object, "stf_components")):
		for component_ref in application_object.stf_components:
			if(hasattr(application_object, component_ref.blender_property_name)):
				components = getattr(application_object, component_ref.blender_property_name)
				for component in components:
					if(component.stf_id == component_ref.stf_id):
						ret.append(component)
	return ret

def import_component_base(component: any, json_resource: any):
	if("name" in json_resource): component.stf_name = json_resource["name"]
	if("overrides" in json_resource):
		for override in json_resource["overrides"]:
			component.overrides.add().target_id = override
	if("enabled" in json_resource):
		component.enabled = json_resource["enabled"]

def export_component_base(stf_type: str, component: any) -> dict:
	ret = { "type": stf_type }
	if(component.stf_name): ret["name"] = component.stf_name
	if(component.overrides): ret["overrides"] = [override.target_id for override in component.overrides]
	if(component.enabled == False): ret["enabled"] = False
	return ret



class ComponentLoadJsonOperatorBase():
	bl_label = "Set from Json"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	json_string: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		try:
			json_resource = json.loads(self.json_string)

			for component in self.get_property(context):
				if(component.stf_id == self.component_id):
					self.parse_json(context, component, json_resource)
					return {"FINISHED"}
		except Exception as e:
			self.report({"ERROR"}, str(e))
		self.report({"ERROR"}, "Failed applying Json values.")
		return {"CANCELLED"}

	def get_property(self, context) -> any:
		pass

	def parse_json(self, context, component: any, json_resource: dict):
		pass

	def draw(self, context):
		layout: bpy.types.UILayout = self.layout
		layout.label(text="Paste json setup string.")
		layout.label(text="(This will overwrite your current values)")
		layout.prop(self, "json_string", text="")


def register():
	bpy.types.Scene.workaround_for_blenders_datamodel__component_overrides = bpy.props.CollectionProperty(type=STF_BlenderComponentOverride) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "workaround_for_blenders_datamodel__component_overrides"):
		del bpy.types.Scene.workaround_for_blenders_datamodel__component_overrides
