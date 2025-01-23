import bpy

from .stf_blender_material_values.color_value import STF_Blender_Material_Value_Module_Color

from . import stf_material_definition as stfmat


def blender_material_to_stf(blender_material: bpy.types.Material) -> stfmat.STF_Material_Definition:
	clear_stf_material(blender_material)

	#add_property(blender_material, "color", STF_Blender_Material_Value_Module_Color)


def clear_stf_material(blender_material: bpy.types.Material):
	blender_material.stf_material.style_hints.clear()
	blender_material.stf_material_properties.clear()
	for mat_value in blender_material.stf_material_property_values:
		if(hasattr(blender_material, mat_value.value_property_name)):
			blender_material[mat_value.value_property_name].clear()
	blender_material.stf_material_property_values.clear()
	blender_material.stf_active_material_property_index = 0


