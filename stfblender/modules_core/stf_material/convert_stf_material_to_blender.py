import bpy


def stf_material_to_blender(blender_material: bpy.types.Material):
	pass


class STFConvertSTFMaterialToBlender(bpy.types.Operator):
	bl_idname = "stf.convert_stf_material_to_blender"
	bl_label = "Convert STF Material to Blender"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		stf_material_to_blender(context.material)
		return {"FINISHED"}
