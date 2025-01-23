import bpy

from .blender_material_matcher_base import Blender_Material_Property_Matcher_Module_Base, add_property, add_value
from ..stf_blender_material_values.color_value import STF_Blender_Material_Value_Module_Color


def _match(blender_material: bpy.types.Material) -> bool:
	prop = add_property(blender_material, "color", STF_Blender_Material_Value_Module_Color)
	value_ref, value = add_value(blender_material, prop, STF_Blender_Material_Value_Module_Color)
	value.color = (blender_material.diffuse_color[0], blender_material.diffuse_color[1], blender_material.diffuse_color[2])
	return True


class Blender_Material_Property_Matcher_Color(Blender_Material_Property_Matcher_Module_Base):
	property_name = "color"
	priority = 0
	match_func = _match
