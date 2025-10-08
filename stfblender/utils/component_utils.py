import bpy
import json
from typing import Callable

from ..exporter.stf_export_context import STF_ExportContext
from ..importer.stf_import_context import STF_ImportContext
from ..base.stf_module_component import STF_BlenderComponentBase, STF_Component_Ref
from ..base.stf_module_data import STF_BlenderDataResourceBase
from ..base.blender_grr.prelude import *
from .id_utils import ensure_stf_id
from .armature_bone import ArmatureBone


def add_component(context_object: any, blender_property_name: str, stf_id: str, stf_type: str, components_ref_property: any = None) -> tuple[STF_Component_Ref, STF_BlenderComponentBase]:
	if(components_ref_property is None):
		if(isinstance(context_object, STF_BlenderDataResourceBase)): # jank, but works
			components_ref_property = context_object.stf_components
			context_object = context_object.id_data
		else:
			components_ref_property = context_object.stf_info.stf_components
	component_ref: STF_Component_Ref = components_ref_property.add()
	component_ref.name = stf_id
	component_ref.stf_id = stf_id
	component_ref.stf_type = stf_type
	component_ref.blender_property_name = blender_property_name

	new_component = getattr(context_object, blender_property_name).add()
	new_component.name = stf_id
	new_component.stf_id = component_ref.stf_id

	if(blender_property_name == "stf_json_fallback_component"):
		new_component.json = "{\"type\": \"" + stf_type + "\"}"

	return (component_ref, new_component)

class STFAddComponentOperatorBase:
	"""Base class to add an STF component to a Blender object"""
	bl_label = "Add Component"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		import uuid
		add_component(self.get_property(context), self.property_name, str(uuid.uuid4()), self.stf_type, self.get_components_ref_property(context))
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass

	def get_components_ref_property(self, context) -> any:
		return self.get_property(context).stf_info.stf_components


class STFRemoveComponentOperatorBase:
	"""Base class to remove an STF component from a Blender object"""
	bl_label = "Remove Component"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
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

	def get_property(self, context) -> any:
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

	def execute(self, context):
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

	def get_property(self, context) -> any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_info.stf_components


class AddOverrideToComponent(bpy.types.Operator):
	"""Add override to component"""
	bl_idname = "stf.add_override_to_component"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	blender_id_type: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	bone_name: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context: bpy.types.Context):
		blender_id = getattr(context, self.blender_id_type.lower())
		if(self.bone_name):
			for bone in blender_id.bones:
				if(bone.name == self.bone_name):
					blender_id = bone
					break
		for component in getattr(blender_id, self.blender_property_name):
			if(component.stf_id == self.component_id):
				override: BlenderGRR = component.overrides.add()
				override.reference_type = "stf_component"
				return {"FINISHED"}
		return {"CANCELLED"}

class RemoveOverrideFromComponent(bpy.types.Operator):
	"""Add override to component"""
	bl_idname = "stf.remove_override_from_component"
	bl_label = "Remove"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	blender_id_type: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	bone_name: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore
	index: bpy.props.IntProperty(default=-1) # type: ignore

	def execute(self, context: bpy.types.Context):
		blender_id = getattr(context, self.blender_id_type.lower())
		if(self.bone_name):
			for bone in blender_id.bones:
				if(bone.name == self.bone_name):
					blender_id = bone
					break
		for component in getattr(blender_id, self.blender_property_name):
			if(component.stf_id == self.component_id):
				component.overrides.remove(self.index)
				return {"FINISHED"}
		return {"CANCELLED"}


def preserve_component_reference(component: STF_BlenderComponentBase, context_object: any) -> Callable:
	if(type(context_object) == bpy.types.Bone):
		armature_bone = ArmatureBone(component.id_data, context_object.name)
		component_id = component.stf_id
		def _get_component() -> STF_BlenderComponentBase:
			for component_ref in armature_bone.get_bone().stf_info.stf_components:
				if(component_ref.stf_id == component_id):
					for component in getattr(armature_bone.get_bone(), component_ref.blender_property_name):
						if(component.stf_id == component_id):
							return component
	else:
		def _get_component() -> STF_BlenderComponentBase:
			return component
	return _get_component


def get_components_from_object(application_object: any) -> list:
	ret = []
	if(hasattr(application_object, "stf_info")):
		for component_ref in application_object.stf_info.stf_components:
			if(hasattr(application_object, component_ref.blender_property_name)):
				components = getattr(application_object, component_ref.blender_property_name)
				for component in components:
					if(component.stf_id == component_ref.stf_id):
						ret.append(component)
	return ret


def import_component_base(context: STF_ImportContext, component: STF_BlenderComponentBase, json_resource: dict, context_object: any = None):
	if("name" in json_resource): component.stf_name = json_resource["name"]
	if("overrides" in json_resource):
		_get_component = preserve_component_reference(component, context_object)

		def _handle():
			component = _get_component()
			for override_id in json_resource["overrides"]:
				#print(override_id)
				override: BlenderGRR = component.overrides.add()
				if(override_resource := context.import_resource(override_id, stf_kind="component")):
					construct_blender_grr(override_resource, override, override_id)
				else: # fallback if something went fucky
					override.reference_type = "stf_component"
					override.stf_component_id = override_id
		context.add_task(_handle)
	if("enabled" in json_resource):
		component.enabled = json_resource["enabled"]

def export_component_base(context: STF_ExportContext, stf_type: str, component: STF_BlenderComponentBase) -> dict:
	ensure_stf_id(context, component, component)
	ret = { "type": stf_type }
	if(component.stf_name): ret["name"] = component.stf_name
	if(component.overrides and len(component.overrides) > 0):
		def _handle():
			overrides_list = []
			for override in component.overrides:
				if(resolved := resolve_blender_grr(override)):
					if(resolved_id := context.serialize_resource(resolved)):
						overrides_list.append(resolved_id)
						continue
				if(override.stf_component_id): # fallback if something went fucky
					overrides_list.append(override.stf_component_id)
			if(len(overrides_list)):
				ret["overrides"] = overrides_list
		context.add_task(_handle)
	if(component.enabled == False): ret["enabled"] = False
	return ret


class ComponentLoadJsonOperatorBase():
	bl_label = "Set from Json"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	component_id: bpy.props.StringProperty() # type: ignore

	json_string: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
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

	def get_property(self, context) -> any:
		pass

	def parse_json(self, context, component: any, json_resource: dict):
		pass

	def draw(self, context):
		layout: bpy.types.UILayout = self.layout
		layout.label(text="Paste json setup string.")
		layout.label(text="(This will overwrite your current values)")

		json_error = False
		try:
			json.loads(self.json_string)
		except:
			json_error = True
		layout.alert = json_error
		layout.prop(self, "json_string", text="", icon="ERROR" if json_error else "NONE")
