import bpy

from ..base.stf_module_data import STF_BlenderDataResourceBase, STF_Data_Ref
from .id_utils import ensure_stf_id


def add_resource(collection: bpy.types.Collection, blender_property_name: str, stf_id: str, stf_type: str) -> tuple[STF_Data_Ref, any]:
	resource_ref: STF_Data_Ref = collection.stf_data_refs.add()
	resource_ref.stf_id = stf_id
	resource_ref.stf_type = stf_type
	resource_ref.blender_property_name = blender_property_name
	resource_ref.name = stf_id

	new_resource = getattr(collection, blender_property_name).add()
	new_resource.stf_id = resource_ref.stf_id
	new_resource.name = stf_id

	if(blender_property_name == "stf_json_fallback_data"):
		new_resource.json = "{\"type\": \"" + stf_type + "\"}"

	return (resource_ref, new_resource)


class STFCreateDataResourceOperator(bpy.types.Operator):
	"""Create a new STF data resource"""
	bl_idname = "stf.create_data_resource"
	bl_label = "Create New Resource"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		import uuid
		add_resource(context.scene.collection if self.use_scene_collection else context.collection, self.property_name, str(uuid.uuid4()), self.stf_type)
		return {"FINISHED"}


class STFRemoveDataResourceOperator(bpy.types.Operator):
	"""Remove this STF data-resource"""
	bl_idname = "stf.remove_data_resource"
	bl_label = "Remove Resource"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	index: bpy.props.IntProperty(name="Resource Index", default=-1) # type: ignore
	property_name: bpy.props.StringProperty() # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		collection = context.scene.collection if self.use_scene_collection else context.collection
		if(hasattr(collection, self.property_name)):
			resource_type_list = getattr(collection, self.property_name)
			for resource_index, resource in enumerate(resource_type_list):
				if(resource.stf_id == collection.stf_data_refs[self.index].stf_id):
					# Remove components
					for component_ref in resource.stf_components:
						for resource_component_index, resource_component in enumerate(getattr(collection, component_ref.blender_property_name)):
							if(resource_component.stf_id == component_ref.stf_id):
								getattr(collection, component_ref.blender_property_name).remove(resource_component_index)
								break
					# Remove resource
					resource_type_list.remove(resource_index)
					break
		# Remove resource reference
		collection.stf_data_refs.remove(self.index)
		return {"FINISHED"}


class STFEditDataResourceOperator(bpy.types.Operator):
	"""Edit the ID of a data-resource"""
	bl_idname = "stf.edit_data_resource"
	bl_label = "Edit ID"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore
	edit_id: bpy.props.StringProperty(name="ID") # type: ignore

	def invoke(self, context, event):
		self.edit_id = self.resource_id

		return context.window_manager.invoke_props_dialog(self)

	def execute(self, context):
		if(not self.edit_id):
			self.report({"ERROR"}, "ID can't be empty!")
			return {"CANCELLED"}

		collection = context.scene.collection if self.use_scene_collection else context.collection

		# let resource_ref
		for resource_ref in collection.stf_data_refs:
			if(resource_ref.stf_id == self.resource_id):
				break
		else:
			self.report({"ERROR"}, "Couldn't change Component ID")
			return {"CANCELLED"}

		resource_type_list = getattr(collection, resource_ref.blender_property_name)
		target_component_index = None
		for index, component in enumerate(resource_type_list):
			if(component.stf_id == resource_ref.stf_id):
				target_component_index = index
				break

		resource_type_list[target_component_index].stf_id = self.edit_id
		resource_type_list[target_component_index].name = self.edit_id
		resource_ref.stf_id = self.edit_id
		resource_ref.name = self.edit_id
		return {"FINISHED"}


	def draw(self, context):
		layout: bpy.types.UILayout = self.layout
		layout.prop(self, "edit_id")


def get_components_from_data_resource(resource: STF_BlenderDataResourceBase) -> list:
	collection = resource.id_data
	ret = []
	for component_ref in resource.stf_components:
		if(hasattr(collection, component_ref.blender_property_name)):
			components = getattr(collection, component_ref.blender_property_name)
			for component in components:
				if(component.stf_id == component_ref.stf_id):
					ret.append(component)
	return ret


def import_data_resource_base(resource: STF_BlenderDataResourceBase, json_resource: any):
	if("name" in json_resource): resource.stf_name = json_resource["name"]

def export_data_resource_base(stf_context: any, stf_type: str, resource: STF_BlenderDataResourceBase) -> dict:
	ensure_stf_id(stf_context, resource, resource)
	ret = { "type": stf_type }
	if(resource.stf_name): ret["name"] = resource.stf_name
	return ret

