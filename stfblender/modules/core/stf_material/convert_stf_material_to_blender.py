import bpy

from .stf_material_definition import STF_Material_Property


def stf_material_to_blender(blender_material: bpy.types.Material):
	blender_material.use_nodes = True
	for node in blender_material.node_tree.nodes:
		blender_material.node_tree.nodes.remove(node)

	output_node = blender_material.node_tree.nodes.new("ShaderNodeOutputMaterial")
	output_node.location.x = 600

	# TODO select shader based on style hints and stuff
	surface = blender_material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
	surface.location.x = 300
	blender_material.node_tree.links.new(surface.outputs[0], output_node.inputs[0])

	parsed_node = 0

	for property in blender_material.stf_material_properties:
		property: STF_Material_Property = property
		if(property.property_type == "albedo.texture" and property.value_type == "image"):
			value_id = property.values[0].value_id
			## let value
			for value in getattr(blender_material, property.value_property_name):
				if(value.value_id == value_id):
					break
			if(value):
				image_node = blender_material.node_tree.nodes.new("ShaderNodeTexImage")
				image_node.location.y = parsed_node * 400
				parsed_node += 1
				image_node.image = value.image
				blender_material.node_tree.links.new(image_node.outputs[0], surface.inputs[0])


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
