import bpy

from ....libstf.stf_export_context import STF_ExportContext
from .stf_material_operators import add_property, clear_stf_material
from .material_value_modules.float_value import STF_Material_Value_Module_Float
from .material_value_modules.color_value import STF_Material_Value_Module_Color
from .material_value_modules.image_value import STF_Material_Value_Module_Image


def convert_principled_bsdf_to_stf(blender_material: bpy.types.Material, node: bpy.types.ShaderNodeBsdfPrincipled):
	hint = blender_material.stf_material.style_hints.add()
	hint.value = "realistic"
	hint = blender_material.stf_material.style_hints.add()
	hint.value = "pbr"

def convert_texture_or_color(blender_material: bpy.types.Material, socket: bpy.types.NodeSocket, texture_property: str, color_property: str):
	if(len(socket.links) == 1):
		if(type(socket.links[0].from_node) is bpy.types.ShaderNodeTexImage):
			texture_node: bpy.types.ShaderNodeTexImage = socket.links[0].from_node
			if(texture_node.image):
				_, _, value = add_property(blender_material, texture_property, STF_Material_Value_Module_Image)
				value.image = texture_node.image
	else:
		if(socket.type == "RGBA"):
			_, _, value = add_property(blender_material, color_property, STF_Material_Value_Module_Color)
			value.color = socket.default_value

def convert_texture_or_float(blender_material: bpy.types.Material, socket: bpy.types.NodeSocket, texture_property: str, float_property: str):
	if(len(socket.links) == 1):
		if(type(socket.links[0].from_node) is bpy.types.ShaderNodeTexImage):
			texture_node: bpy.types.ShaderNodeTexImage = socket.links[0].from_node
			if(texture_node.image):
				_, _, value = add_property(blender_material, texture_property, STF_Material_Value_Module_Image)
				value.image = texture_node.image
	else:
		if(socket.type == "VALUE"):
			_, _, value = add_property(blender_material, float_property, STF_Material_Value_Module_Float)
			value.number = socket.default_value


def convert_shader_node_to_stf(blender_material: bpy.types.Material, node: bpy.types.ShaderNode):
	print()
	if("Base Color" in node.inputs):
		convert_texture_or_color(blender_material, node.inputs["Base Color"], "albedo.texture", "albedo.color")
	if("Roughness" in node.inputs):
		convert_texture_or_float(blender_material, node.inputs["Roughness"], "roughness.texture", "roughness.value")


def blender_material_to_stf(blender_material: bpy.types.Material):
	clear_stf_material(blender_material)

	if(blender_material.use_nodes):
		output_node = blender_material.node_tree.get_output_node("ALL")

		if(len(output_node.inputs["Surface"].links) == 1):
			if(type(output_node.inputs["Surface"].links[0].from_node) is bpy.types.ShaderNodeBsdfPrincipled):
				convert_principled_bsdf_to_stf(blender_material, output_node.inputs["Surface"].links[0].from_node)

			if(issubclass(type(output_node.inputs["Surface"].links[0].from_node), bpy.types.ShaderNode)):
				convert_shader_node_to_stf(blender_material, output_node.inputs["Surface"].links[0].from_node)


	else:
		_, _, value = add_property(blender_material, "albedo.color", STF_Material_Value_Module_Color)
		value.color = blender_material.diffuse_color



class STFConvertBlenderMaterialToSTF(bpy.types.Operator):
	bl_idname = "stf.convert_blender_material_to_stf"
	bl_label = "Convert Blender Material to STF"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		blender_material_to_stf(context.material)
		return {"FINISHED"}
