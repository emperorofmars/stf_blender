import bpy

from ..stf_material_definition import STF_Material_Value_Base


class STF_Material_Value_Int(STF_Material_Value_Base):
	number: bpy.props.IntProperty(name="Number") # type: ignore


def register():
	bpy.types.Material.stf_material_value_int = bpy.props.CollectionProperty(type=STF_Material_Value_Int, name="Number Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_int"):
		del bpy.types.Material.stf_material_value_int
