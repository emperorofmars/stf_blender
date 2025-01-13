import bpy

class SetActiveObjectOperator(bpy.types.Operator):
	"""Select the specified object in the scene"""
	bl_idname = "stf.util_set_object_active"
	bl_label = "Select"
	bl_options = {"REGISTER", "UNDO"}

	target_name: bpy.props.StringProperty(name = "target_name") # type: ignore

	def execute(self, context):
		blender_object = bpy.data.objects.get(self.target_name)
		for selected in bpy.context.selected_objects:
			selected.select_set(False)
		blender_object.select_set(True)
		bpy.context.view_layer.objects.active = blender_object
		return {"FINISHED"}
