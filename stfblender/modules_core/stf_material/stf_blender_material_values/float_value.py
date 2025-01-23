import bpy

from ..stf_material_definition import STF_Material_Value_Base


class STF_Material_Value_Float(STF_Material_Value_Base):
	number: bpy.props.FloatProperty(name="Number") # type: ignore


def register():
	bpy.types.Material.stf_material_value_float = bpy.props.CollectionProperty(type=STF_Material_Value_Float, name="Number Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_float"):
		del bpy.types.Material.stf_material_value_float
