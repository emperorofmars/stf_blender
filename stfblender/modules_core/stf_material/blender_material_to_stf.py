import bpy

from .stf_material_operators import add_property, clear_stf_material
from .material_value_modules.color_value import STF_Material_Value_Module_Color
from . import stf_material_definition as stfmat


def blender_material_to_stf(blender_material: bpy.types.Material) -> stfmat.STF_Material_Definition:
	clear_stf_material(blender_material)

	add_property(blender_material, "color", STF_Material_Value_Module_Color)
