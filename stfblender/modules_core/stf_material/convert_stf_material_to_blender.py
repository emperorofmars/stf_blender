import bpy


def stf_material_to_blender(blender_material: bpy.types.Material):
	blender_material.use_nodes = True
	output_node = blender_material.node_tree.get_output_node("ALL")
	for node in blender_material.node_tree.nodes:
		if(node != output_node):
			blender_material.node_tree.nodes.remove(node)
	# TODO select shader based on style hints and stuff
	surface = blender_material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
	blender_material.node_tree.links.new(surface.outputs[0], output_node.inputs[0])

	# TODO parse stf material


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
