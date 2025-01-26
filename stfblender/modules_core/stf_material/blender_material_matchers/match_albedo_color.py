import bpy

from .blender_material_matcher_base import Blender_Material_Property_Matcher_Module_Base
from ..stf_material_definition import add_property
from ..stf_blender_material_values.color_value import STF_Material_Value_Module_Color


_property_type = "albedo_color"


def _match(blender_material: bpy.types.Material) -> bool:
	prop, value_ref, value = add_property(blender_material, _property_type, STF_Material_Value_Module_Color)
	value.color = (blender_material.diffuse_color[0], blender_material.diffuse_color[1], blender_material.diffuse_color[2])
	return True


class Blender_Material_Property_Matcher_Color(Blender_Material_Property_Matcher_Module_Base):
	property_type = _property_type
	priority = 0
	match_func = _match
