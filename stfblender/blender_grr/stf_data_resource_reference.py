import bpy

from ..base.stf_module_data import STF_BlenderDataResourceBase, STF_Data_Ref

"""
Blender Data-Resource Reference

Bringing polymorphism to Blender
"""

class STFDataResourceReference(bpy.types.PropertyGroup):
	use_scene_collection: bpy.props.BoolProperty(default=False, name="Use Scene Collection") # type: ignore
	scene: bpy.props.PointerProperty(type=bpy.types.Scene, name="Scene") # type: ignore
	collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection") # type: ignore
	stf_data_resource_id: bpy.props.StringProperty(name="Resource ID") # type: ignore


def __draw_blender_collection_selection(layout: bpy.types.UILayout, drr: STFDataResourceReference) -> bpy.types.Collection:
	layout.prop(drr, "use_scene_collection")
	if(not drr.use_scene_collection):
		layout.prop(drr, "collection")
		return drr.collection
	else:
		layout.prop(drr, "scene")
		return drr.scene.collection if drr.scene else None

def draw_blender_drr(layout: bpy.types.UILayout, drr: STFDataResourceReference, type_filter: list[str] = []):
	if(collection := __draw_blender_collection_selection(layout, drr)):

		for resource_ref in collection.stf_data_refs:
			if(resource_ref.stf_id == drr.stf_data_resource_id):
				break
		for resource in collection.dev_vrm_blendshape_pose:
			if(resource.stf_id == drr.stf_data_resource_id):
				break

		layout.prop_search(drr, "stf_data_resource_id", collection, "stf_data_refs", icon="ERROR" if resource_ref and type_filter and resource_ref.stf_type not in type_filter else "NONE")
		row = layout.row()
		if(resource_ref and type_filter and resource_ref.stf_type not in type_filter):
			row.label(text="Invalid Type: " + resource_ref.stf_type, icon="ERROR")
		elif(resource_ref and resource):
			row.label(text="Selected: " + resource_ref.stf_type, icon="INFO")
			row.label(text="Name: " + resource.stf_name)


def __get_blender_property(ref_holder: any, property_holder: any, target_id: str) -> tuple[STF_Data_Ref, STF_BlenderDataResourceBase]:
	for resource_ref in ref_holder:
		if(resource_ref.stf_id == target_id):
			for resource in getattr(property_holder, resource_ref.blender_property_name):
				if(resource.stf_id == resource_ref.stf_id):
					return resource_ref, resource
	return None

def resolve_blender_drr(drr: STFDataResourceReference) -> tuple[STF_Data_Ref, STF_BlenderDataResourceBase]:
	if(drr.use_scene_collection and drr.scene):
		return __get_blender_property(drr.scene.collection.stf_data_refs, drr.scene.collection, drr.stf_data_resource_id)
	elif(not drr.use_scene_collection and drr.collection):
		return __get_blender_property(drr.collection.stf_data_refs, drr.collection, drr.stf_data_resource_id)
	else:
		return None

def is_blender_drr_valid(drr: STFDataResourceReference, valid_types: list[str] = []) -> bool:
	if(res := resolve_blender_drr(drr)):
		resource_ref, resource = res
		if(not valid_types or resource_ref.stf_type in valid_types):
			return True
	return False
