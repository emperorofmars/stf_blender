import bpy

from .material_property_module_base import Material_Property_Module_Base
from ..material_value_modules.color_value import STF_Material_Value_Module_Color
from ..stf_material_operators import add_property


_property_type = "albedo_color"


def _from_blender_func(blender_material: bpy.types.Material) -> bool:
	prop, value_ref, value = add_property(blender_material, _property_type, STF_Material_Value_Module_Color)
	value.color = (blender_material.diffuse_color[0], blender_material.diffuse_color[1], blender_material.diffuse_color[2])
	return True


class Blender_Material_Property_Matcher_Color(Material_Property_Module_Base):
	property_type = _property_type
	priority = 0
	from_blender_func = _from_blender_func
	to_blender_func = None
	draw_func = None
