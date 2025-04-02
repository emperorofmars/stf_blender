import bpy

from .material_property_module_base import Material_Property_Module_Base
from ..material_value_modules.color_value import STF_Material_Value_Module_Color
from ..stf_material_operators import add_property


_property_group = "albedo"
_property_type_color = "albedo.color"


def _from_blender_func(blender_material: bpy.types.Material) -> bool:
	prop, value_ref, value = add_property(blender_material, _property_type_color, STF_Material_Value_Module_Color, _property_group)
	# This is bullshit
	value.color = (blender_material.diffuse_color[0], blender_material.diffuse_color[1], blender_material.diffuse_color[2])

	# TODO figure this out properly
	#blender_material.node_tree.get_output_node("ALL").color
	return True


class Blender_Material_Property_Module_Color(Material_Property_Module_Base):
	property_group = _property_group
	priority = 0
	from_blender_func = _from_blender_func
	to_blender_func = None
