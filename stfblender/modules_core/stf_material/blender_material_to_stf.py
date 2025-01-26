import bpy

from .material_value_modules.color_value import STF_Material_Value_Module_Color

from . import stf_material_definition as stfmat


def blender_material_to_stf(blender_material: bpy.types.Material) -> stfmat.STF_Material_Definition:
	stfmat.clear_stf_material(blender_material)

	stfmat.add_property(blender_material, "color", STF_Material_Value_Module_Color)
