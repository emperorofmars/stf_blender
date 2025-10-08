import bpy

"""
STF Data-Resource Reference

Bringing polymorphism to Blender
"""

class STFDataResourceReference(bpy.types.PropertyGroup):
	use_scene_collection: bpy.props.BoolProperty(default=False, name="Use Scene Collection") # type: ignore
	scene: bpy.props.PointerProperty(type=bpy.types.Scene, name="Scene") # type: ignore
	collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection") # type: ignore
	stf_data_resource_id: bpy.props.StringProperty(name="Resource ID") # type: ignore

