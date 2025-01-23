from typing import Callable
import bpy

from ..stf_material_definition import STF_Blender_Material_Value_Module_Base, STF_Material_Property, STF_Material_Value_Ref


class Blender_Material_Property_Matcher_Module_Base:
	property_name: str
	priority: int = 0
	match_func: Callable[[bpy.types.Material], bool]


def add_property(blender_material: bpy.types.Material, property_type: str, value_module: STF_Blender_Material_Value_Module_Base) -> tuple[STF_Material_Property, STF_Material_Value_Ref, STF_Blender_Material_Value_Module_Base]:
	prop = blender_material.stf_material_properties.add()
	prop.property_type = property_type
	prop.value_property_name = value_module.property_name

	value_ref, value = add_value_to_property(blender_material, prop, value_module)
	return prop, value_ref, value


def add_value_to_property(blender_material: bpy.types.Material, property: STF_Material_Property, value_module: STF_Blender_Material_Value_Module_Base) -> tuple[STF_Material_Value_Ref, STF_Blender_Material_Value_Module_Base]:
	value_ref = property.values.add()
	value_ref.value_property_name = value_module.property_name
	max_id = 0
	for value in value_ref.value_property_name:
		if(value.value_id > max_id): max_id = value.value_id + 1
	value_ref.value_id = max_id
	value = blender_material[value_module.property_name].add()
	value.value_id = max_id
	return value_ref, value
