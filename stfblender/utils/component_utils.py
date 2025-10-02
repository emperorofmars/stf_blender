import json
import bpy

from ..base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, STF_BlenderComponentOverride
from ..base.stf_module_data import STF_BlenderDataResourceBase
from ..utils.id_utils import ensure_stf_id


def find_component_module(stf_modules: list[STF_BlenderComponentModule], stf_type: str) -> STF_BlenderComponentModule:
	for stf_module in stf_modules:
		if(stf_module.stf_type == stf_type):
			return stf_module


def add_component(context_object: any, blender_property_name: str, stf_id: str, stf_type: str, components_ref_property: any = None) -> tuple[STF_Component_Ref, STF_BlenderComponentBase]:
	if(components_ref_property is None):
		if(isinstance(context_object, STF_BlenderDataResourceBase)): # jank, but works
			components_ref_property = context_object.stf_components
			context_object = context_object.id_data
		else:
			components_ref_property = context_object.stf_info.stf_components
	component_ref: STF_Component_Ref = components_ref_property.add()
	component_ref.stf_id = stf_id
	component_ref.stf_type = stf_type
	component_ref.blender_property_name = blender_property_name
	component_ref.name = stf_id

	new_component = getattr(context_object, blender_property_name).add()
	new_component.stf_id = component_ref.stf_id
	new_component.name = stf_id

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
							component.overrides.clear()
							for override in context.scene.workaround_for_blenders_datamodel__component_overrides:
								if(override.target_id):
									component.overrides.add().target_id = override.target_id
							return {"FINISHED"}

		self.report({"ERROR"}, "Couldn't change Component ID")
		return {"CANCELLED"}

	def draw(self, context):
		layout: bpy.types.UILayout = self.layout
		layout.prop(self, "edit_component_id")

		layout.label(text="Overrides:")
		for index, override in enumerate(context.scene.workaround_for_blenders_datamodel__component_overrides):
			row = layout.row()
			row.prop(override, "target_id", text="Target ID")
			row.operator(RemoveOverrideFromComponent.bl_idname, text="", icon="X").index = index
		layout.operator(AddOverrideToComponent.bl_idname)

	def get_property(self, context) -> any:
		pass

	def get_components_ref_property(self, context) -> STF_Component_Ref:
		return self.get_property(context).stf_info.stf_components


class AddOverrideToComponent(bpy.types.Operator):
	"""Add override to component"""
	bl_idname = "stf.add_override_to_component"
	bl_label = "Add"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def execute(self, context):
		bpy.context.scene.workaround_for_blenders_datamodel__component_overrides.add()
		return {"FINISHED"}

class RemoveOverrideFromComponent(bpy.types.Operator):
	"""Add override to component"""
	bl_idname = "stf.remove_override_from_component"
	bl_label = "Remove"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	index: bpy.props.IntProperty(default=-1) # type: ignore

	def execute(self, context):
		bpy.context.scene.workaround_for_blenders_datamodel__component_overrides.remove(self.index)
		return {"FINISHED"}


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

def import_component_base(component: any, json_resource: any):
	if("name" in json_resource): component.stf_name = json_resource["name"]
	if("overrides" in json_resource):
		for override in json_resource["overrides"]:
			component.overrides.add().target_id = override
	if("enabled" in json_resource):
		component.enabled = json_resource["enabled"]

def export_component_base(stf_context: any, stf_type: str, component: any) -> dict:
	ensure_stf_id(stf_context, component, component)
	ret = { "type": stf_type }
	if(component.stf_name): ret["name"] = component.stf_name
	if(component.overrides): ret["overrides"] = [override.target_id for override in component.overrides]
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


def register():
	bpy.types.Scene.workaround_for_blenders_datamodel__component_overrides = bpy.props.CollectionProperty(type=STF_BlenderComponentOverride, options=set()) # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "workaround_for_blenders_datamodel__component_overrides"):
		del bpy.types.Scene.workaround_for_blenders_datamodel__component_overrides
