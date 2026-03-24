import bpy
from typing import Any
from collections.abc import Sequence

from .stf_data_resource_reference import STFDataResourceReference
from ..resource.data.stf_handler_data import STF_DataResourceBase, STF_Data_Ref

"""
STF Data-Resource Reference

Bringing polymorphism to Blender
"""

def __draw_blender_collection_selection(layout: bpy.types.UILayout, drr: STFDataResourceReference) -> bpy.types.Collection:
	layout.prop(drr, "use_scene_collection")
	if(not drr.use_scene_collection):
		layout.prop(drr, "collection")
		return drr.collection
	else:
		layout.prop(drr, "scene")
		return drr.scene.collection if drr.scene else None

def draw_stf_data_resource_reference(layout: bpy.types.UILayout, drr: STFDataResourceReference, type_filter: Sequence[str] = ()):
	if(collection := __draw_blender_collection_selection(layout, drr)):
		# let resource_ref
		for resource_ref in collection.stf_data_refs:
			if(resource_ref.stf_id == drr.stf_data_resource_id):
				break
		else:
			resource_ref = None
		# let resource
		if(resource_ref):
			for resource in getattr(collection, resource_ref.blender_property_name):
				if(resource.stf_id == drr.stf_data_resource_id):
					break
		else:
			resource = None

		layout.prop_search(drr, "stf_data_resource_id", collection, "stf_data_refs", icon="ERROR" if not resource_ref or type_filter and resource_ref.stf_type not in type_filter else "NONE")

		if(resource_ref and type_filter and resource_ref.stf_type not in type_filter):
			info_layout = layout
			if(layout.use_property_split):
				split = layout.split(factor=0.4)
				split.row()
				info_layout = split.row()
			info_layout.label(text="Invalid Type: " + resource_ref.stf_type, icon="ERROR")
		elif(resource_ref and resource):
			info_layout = layout
			if(layout.use_property_split):
				split = layout.split(factor=0.4)
				split.row()
				info_layout = split.row()
			info_layout.label(text=resource_ref.stf_type + " - " + (resource.stf_name if resource.stf_name and len(resource.stf_name) > 0 else "Unnamed"))


def __get_blender_property(ref_holder: Any, property_holder: Any, target_id: str) -> tuple[STF_Data_Ref, STF_DataResourceBase]:
	for resource_ref in ref_holder:
		if(resource_ref.stf_id == target_id):
			for resource in getattr(property_holder, resource_ref.blender_property_name):
				if(resource.stf_id == resource_ref.stf_id):
					return resource_ref, resource
	return None

def resolve_stf_data_resource_reference(drr: STFDataResourceReference) -> tuple[STF_Data_Ref, STF_DataResourceBase]:
	if(drr.use_scene_collection and drr.scene):
		return __get_blender_property(drr.scene.collection.stf_data_refs, drr.scene.collection, drr.stf_data_resource_id)
	elif(not drr.use_scene_collection and drr.collection):
		return __get_blender_property(drr.collection.stf_data_refs, drr.collection, drr.stf_data_resource_id)
	else:
		return None

def resolve_stf_data_resource_holder(drr: STFDataResourceReference) -> bpy.types.Collection:
	if(drr.use_scene_collection and drr.scene):
		return drr.scene.collection
	elif(not drr.use_scene_collection and drr.collection):
		return drr.collection
	else:
		return None

def validate_stf_data_resource_reference(drr: STFDataResourceReference, valid_types: Sequence[str] = ()) -> bool:
	if(drr):
		if(res := resolve_stf_data_resource_reference(drr)):
			resource_ref, _resource = res
			if(not valid_types or resource_ref.stf_type in valid_types):
				return True
	return False

def pretty_print_data_resource_reference(drr: STFDataResourceReference) -> str:
	ret = ""
	if(drr.use_scene_collection and drr.scene):
		ret = "Scene Collection / STF Data Resources / " + drr.stf_data_resource_id
	elif(not drr.use_scene_collection and drr.collection):
		ret = "Collection \"" + drr.collection.name + "\" / STF Data Resources / "
	else:
		return "Invalid"

	if(res := resolve_stf_data_resource_reference(drr)):
		_, resource = res
		return ret + (resource.stf_name if resource.stf_name else resource.stf_id)
	else:
		return "Invalid"
