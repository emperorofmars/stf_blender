import bpy

def register():
	bpy.types.Scene.stf_root_collection = bpy.props.PointerProperty(type=bpy.types.Collection, name="Root Collection") # type: ignore

def unregister():
	if hasattr(bpy.types.Scene, "stf_root_collection"):
		del bpy.types.Scene.stf_root_collection
