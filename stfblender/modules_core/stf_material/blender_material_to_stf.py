import bpy

from . import stf_material_definition as stfmat


def blender_material_to_stf(blender_material: bpy.types.Material) -> stfmat.STF_Material_Definition:
	blender_material.stf_material = stfmat.STF_Material_Definition()

	color_prop = blender_material.stf_material.properties.add()
	color_prop.type = "stf.albedo.color"

	#ret["color"] = blender_material.diffuse_color
