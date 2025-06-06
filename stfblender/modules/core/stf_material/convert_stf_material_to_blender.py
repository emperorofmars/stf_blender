import bpy

from .stf_material_definition import STF_Material_Property


def set_image_value(blender_material: bpy.types.Material, surface: bpy.types.ShaderNode, property: STF_Material_Property, target_input: str | int, position_index_v = 0, position_index_h = 0) -> bool:
	property: STF_Material_Property = property
	if(property.value_type == "image"):
		value_id = property.values[0].value_id
		## let value
		for value in getattr(blender_material, property.value_property_name):
			if(value.value_id == value_id):
				break
		if(value):
			image_node: bpy.types.ShaderNodeTexImage = blender_material.node_tree.nodes.new("ShaderNodeTexImage")
			image_node.location.y = position_index_v * -300
			image_node.location.x = position_index_h * -400
			image_node.image = value.image
			blender_material.node_tree.links.new(image_node.outputs[0], surface.inputs[target_input])
			return True
	return False


def stf_material_to_blender(blender_material: bpy.types.Material):
	blender_material.use_nodes = True
	for node in blender_material.node_tree.nodes:
		blender_material.node_tree.nodes.remove(node)

	output_node = blender_material.node_tree.nodes.new("ShaderNodeOutputMaterial")
	output_node.location.x = 800

	# TODO select shader based on style hints and stuff
	surface = blender_material.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
	surface.location.x = 500
	blender_material.node_tree.links.new(surface.outputs[0], output_node.inputs[0])

	node_position_index = 0

	for property in blender_material.stf_material_properties:
		property: STF_Material_Property = property
		if(property.property_type == "albedo.texture" and property.value_type == "image"):
			node_position_index += set_image_value(blender_material, surface, property, "Base Color", position_index_v = node_position_index)
		elif(property.property_type == "roughness.texture" and property.value_type == "image"):
			node_position_index += set_image_value(blender_material, surface, property, "Roughness", position_index_v = node_position_index)
		elif(property.property_type == "metallic.texture" and property.value_type == "image"):
			node_position_index += set_image_value(blender_material, surface, property, "Metallic", position_index_v = node_position_index)
		elif(property.property_type == "normal.texture" and property.value_type == "image"):
			normal_node = blender_material.node_tree.nodes.new("ShaderNodeNormalMap")
			normal_node.location.y = node_position_index * -300
			blender_material.node_tree.links.new(normal_node.outputs[0], surface.inputs["Normal"])
			node_position_index += set_image_value(blender_material, normal_node, property, "Color" ,position_index_v = node_position_index, position_index_h = 1)
			node_position_index += 1

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
