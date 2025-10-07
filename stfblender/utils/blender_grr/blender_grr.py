import bpy

from .stf_data_resource_reference import STFDataResourceReference, draw_stf_data_resource_reference, resolve_stf_data_resource_reference, validate_stf_data_resource_reference
from .blender_resource_reference import BlenderResourceReference, blender_type_values, draw_blender_resource_reference, resolve_blender_resource_reference, validate_blender_resource_reference

"""
Blender Generic Resource Reference

Bringing polymorphism to Blender

This is a big TODO, making this complete, user friendly and nice to handle will take effort.
"""

reference_type_values = (
	("blender", "Blender Native Resource", "Objects, Meshes, Armatures, etc.."),
	("stf_data_resource", "STF-Data Resource", "STF Resources not natively supported by Blender"),
	("stf_component", "STF Component", "STF Components on a native Blender or STF-Data Resource"),
)

class BlenderGRR(bpy.types.PropertyGroup):
	reference_type: bpy.props.EnumProperty(name="Reference Type", items=reference_type_values) # type: ignore

	blender_type: bpy.props.EnumProperty(name="Type", items=blender_type_values) # type: ignore

	blender_resource_reference: bpy.props.PointerProperty(type=BlenderResourceReference, name="Blender Resource Reference") # type: ignore
	stf_data_resource_reference: bpy.props.PointerProperty(type=STFDataResourceReference, name="STF Data-Resource Reference") # type: ignore


	stf_data_resource_id: bpy.props.StringProperty(name="Resource ID") # type: ignore
	stf_component_id: bpy.props.StringProperty(name="Component ID") # type: ignore


def draw_blender_grr(layout: bpy.types.UILayout, grr: BlenderGRR):
	layout.prop(grr, "reference_type")

	match(grr.reference_type):
		case "blender": draw_blender_resource_reference(layout, grr.blender_resource_reference)
		case "stf_data_resource": draw_stf_data_resource_reference(layout, grr.stf_data_resource_reference)
		case "stf_component": pass

def resolve_blender_grr(grr: BlenderGRR) -> any:
	match(grr.reference_type):
		case "blender": return resolve_blender_resource_reference(grr.blender_resource_reference)
		case "stf_data_resource":
			ret = resolve_stf_data_resource_reference(grr.stf_data_resource_reference)
			if(ret):
				return ret[1]
		case "stf_component": pass
	return None

def validate_blender_grr(grr: BlenderGRR) -> bool:
	if(not grr):
		return False
	match(grr.reference_type):
		case "blender": return validate_blender_resource_reference(grr.blender_resource_reference)
		case "stf_data_resource": return validate_stf_data_resource_reference(grr.stf_data_resource_reference)
		case "stf_component": pass
	return False
