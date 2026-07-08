import bpy


def register():
	bpy.types.Scene.stf_edit_resource_id = bpy.props.BoolProperty(name="Edit ID", description="Toggle the editing of the ID", default=False)

def unregister():
	if hasattr(bpy.types.Scene, "stf_edit_resource_id"):
		del bpy.types.Scene.stf_edit_resource_id
