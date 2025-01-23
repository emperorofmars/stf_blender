import bpy

from .stf_blender_material_values.color_value import STF_Blender_Material_Value_Module_Color

from . import stf_material_definition as stfmat


def blender_material_to_stf(blender_material: bpy.types.Material) -> stfmat.STF_Material_Definition:
	clear_stf_material(blender_material)

	stfmat.add_property(blender_material, "color", STF_Blender_Material_Value_Module_Color)


def clear_stf_material(blender_material: bpy.types.Material):
	blender_material.stf_material.style_hints.clear()
	for mat_property in blender_material.stf_material_properties:
		if(hasattr(blender_material, mat_property.value_property_name)):
			getattr(blender_material, mat_property.value_property_name).clear()
	blender_material.stf_material_property_value_refs.clear()
	blender_material.stf_active_material_property_index = 0
	blender_material.stf_material_properties.clear()


