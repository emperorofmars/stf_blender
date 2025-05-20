import bpy

from ....libstf.stf_export_context import STF_ExportContext
from .stf_material_operators import add_property, clear_stf_material
from .material_value_modules.color_value import STF_Material_Value_Module_Color
from .material_value_modules.image_value import STF_Material_Value_Module_Image
from . import stf_material_definition as stfmat


def convert_principled_bsdf_to_stf(context: STF_ExportContext, blender_material: bpy.types.Material, node: bpy.types.ShaderNodeBsdfPrincipled):
	hint = blender_material.stf_material.style_hints.add()
	hint.value = "realistic"



def convert_shader_node_to_stf(context: STF_ExportContext, blender_material: bpy.types.Material, node: bpy.types.ShaderNode):
	print()
	if("Base Color" in node.inputs and len(node.inputs["Base Color"].links) == 1):
		if(type(node.inputs["Base Color"].links[0].from_node) is bpy.types.ShaderNodeTexImage):
			texture_node: bpy.types.ShaderNodeTexImage = node.inputs["Base Color"].links[0].from_node
			if(texture_node.image):
				_, _, value = add_property(blender_material, "albedo.texture", STF_Material_Value_Module_Image)
				print("texture_node.image")
				print(texture_node.image)
				print(value)
				value.image = texture_node.image
	else:
		if(node.inputs["Base Color"].type == "RGBA"):
			_, _, value = add_property(blender_material, "albedo.color", STF_Material_Value_Module_Color)
			value.color = node.inputs["Base Color"].default_value

	#for input in node.inputs:
		#print(input)


def blender_material_to_stf(context: STF_ExportContext, blender_material: bpy.types.Material):
	clear_stf_material(blender_material)

	if(blender_material.use_nodes):
		output_node = blender_material.node_tree.get_output_node("ALL")

		if(len(output_node.inputs["Surface"].links) == 1):
			if(type(output_node.inputs["Surface"].links[0].from_node) is bpy.types.ShaderNodeBsdfPrincipled):
				convert_principled_bsdf_to_stf(context, blender_material, output_node.inputs["Surface"].links[0].from_node)

			if(issubclass(type(output_node.inputs["Surface"].links[0].from_node), bpy.types.ShaderNode)):
				convert_shader_node_to_stf(context, blender_material, output_node.inputs["Surface"].links[0].from_node)


	else:
		_, _, value = add_property(blender_material, "albedo.color", STF_Material_Value_Module_Color)
		value.color = blender_material.diffuse_color
