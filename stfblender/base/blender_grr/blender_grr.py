import bpy

from .stf_data_resource_reference import STFDataResourceReference
from .blender_resource_reference import BlenderResourceReference

"""
Blender Generic Resource Reference

Bringing polymorphism to Blender

It works right now, however making this actually user friendly and nice to handle will take some more effort.
"""

reference_type_values = (
	("blender", "Blender Native Resource", "Objects, Meshes, Armatures, etc.."),
	("stf_data_resource", "STF Resource", "STF Resources not natively supported by Blender"),
	("stf_component", "STF Component", "STF Components on a native Blender or STF-Data Resource"),
)
component_reference_type_values = (
	("blender", "Blender Native Resource", "Objects, Meshes, Armatures, etc.."),
	("stf_data_resource", "STF Resource", "STF Resources not natively supported by Blender"),
)

class BlenderGRR(bpy.types.PropertyGroup):
	reference_type: bpy.props.EnumProperty(name="Reference Type", items=reference_type_values) # type: ignore

	blender_resource_reference: bpy.props.PointerProperty(type=BlenderResourceReference, name="Blender Resource Reference") # type: ignore
	stf_data_resource_reference: bpy.props.PointerProperty(type=STFDataResourceReference, name="STF Data-Resource Reference") # type: ignore

	component_reference_type: bpy.props.EnumProperty(name="Component From", items=component_reference_type_values) # type: ignore
	stf_component_id: bpy.props.StringProperty(name="Component ID") # type: ignore

