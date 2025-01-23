import bpy

from . import stf_material_definition as stfmat


def blender_material_to_stf(blender_material: bpy.types.Material) -> stfmat.STF_Material_Definition:
	#blender_material.stf_material = stfmat.STF_Material_Definition()

	# TODO clear stf_material, stf_material_properties, stf_material_property_values and all of the actual values reffered to,

	blender_material.stf_material.style_hints.clear()
	blender_material.stf_material_properties.clear()
	for mat_value in blender_material.stf_material_property_values:
		if(hasattr(blender_material, mat_value.value_property_name)):
			blender_material[mat_value.value_property_name].clear()
	blender_material.stf_material_property_values.clear()
	blender_material.stf_active_material_property_index = 0

	color_prop = blender_material.stf_material_properties.add()
	color_prop.property_type = "color"
	color_value_ref = color_prop.values.add()
	color_value_ref.value_property_name = "stf_material_value_color"
	color_value_ref.value_id = 0 # TODO determine current ID and add 1 to it
	color_value = blender_material.stf_material_value_color.add()
	color_value.id = color_value_ref.value_id
	color_value.color = blender_material.diffuse_color[:3] # TODO convert to vector
