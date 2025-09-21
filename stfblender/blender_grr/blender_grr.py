import bpy

from .data_resource_reference import BlenderDRR
from .blender_resource_reference import BlenderResourceReference, blender_type_values

"""
Blender Generic Resource Reference

Bringing polymorphism to Blender

This is a big TODO, making this complete, user friendly and nice to handle will take effort.
"""


reference_type_values = (
	("blender", "Blender Native Resource", ""),
	("stf_component", "STF Component on Blender Resource", ""),
	("stf_data_resource", "STF Data Resource", ""),
	("stf_data_resource_component", "STF Component on STF Data Resource", ""),
)


class BlenderGRR(bpy.types.PropertyGroup):
	reference_type: bpy.props.EnumProperty(name="Reference Type", items=reference_type_values) # type: ignore

	blender_type: bpy.props.EnumProperty(name="Type", items=blender_type_values) # type: ignore

	data_resource_reference: bpy.props.PointerProperty(type=BlenderDRR, name="STF Data-Resource Reference") # type: ignore
	blender_resource_reference: bpy.props.PointerProperty(type=BlenderResourceReference, name="Blender Resource Reference") # type: ignore


	stf_data_resource_id: bpy.props.StringProperty(name="Resource ID") # type: ignore
	stf_component_id: bpy.props.StringProperty(name="Component ID") # type: ignore


def __draw_blender_collection_selection(layout: bpy.types.UILayout, grr: BlenderGRR) -> bool:
	layout.prop(grr, "use_scene_collection")
	if(not grr.use_scene_collection):
		layout.prop(grr, "collection")
		return bool(grr.collection)
	else:
		layout.prop(grr, "scene")
		return bool(grr.scene)


def __draw_blender_type_selection(layout: bpy.types.UILayout, grr: BlenderGRR) -> bool:
	layout.prop(grr, "blender_type")
	if(grr.blender_type == "COLLECTION"):
		return __draw_blender_collection_selection(layout, grr)
	elif(grr.blender_type == "OBJECT"):
		layout.prop(grr, "object")
		return bool(grr.object)

	# todo everything else
	return False


def draw_blender_grr(layout: bpy.types.UILayout, grr: BlenderGRR):
	layout.prop(grr, "reference_type")

	if(grr.reference_type == "stf_component"):
		if(__draw_blender_type_selection(layout, grr)):
			layout.prop(grr, "stf_component_id")
	elif(grr.reference_type == "stf_data_resource"):
		if(__draw_blender_collection_selection(layout, grr)):
			layout.prop(grr, "stf_data_resource_id")
	elif(grr.reference_type == "stf_data_resource_component"):
		if(__draw_blender_collection_selection(layout, grr)):
			layout.prop(grr, "stf_data_resource_id")
			if(grr.stf_data_resource_id):
				layout.prop(grr, "stf_component_id")


def __get_blender_property(holder: any, ref_holder: any, property_holder: any, target_id: str):
	for resource_ref in ref_holder:
		if(resource_ref.stf_id == target_id):
			for resource in getattr(property_holder, resource_ref.blender_property_name):
				if(resource.stf_id == resource_ref.stf_id):
					return resource
	return None


def resolve_blender_grr(grr: BlenderGRR) -> any:
	if(grr.reference_type == "blender"):
		pass # todo return the resource based on the blender_type
	elif(grr.reference_type == "stf_component"):
		pass
	elif(grr.reference_type == "stf_data_resource"):
		if(grr.use_scene_collection and grr.scene):
			return __get_blender_property(grr.scene.collection, grr.scene.collection.stf_data_refs, grr.scene.collection, grr.stf_data_resource_id)
		elif(grr.collection):
			return __get_blender_property(grr.collection, grr.collection.stf_data_refs, grr.collection, grr.stf_data_resource_id)
	elif(grr.reference_type == "stf_data_resource_component"):
		pass
	return None

