import bpy

from ..stf_material_definition import STF_Material_Value_Base


class STF_Material_Value_Color(STF_Material_Value_Base):
	color: bpy.props.FloatVectorProperty(name="Color") # type: ignore


def register():
	bpy.types.Material.stf_material_value_color = bpy.props.CollectionProperty(type=STF_Material_Value_Color, name="Color Value")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_color"):
		del bpy.types.Material.stf_material_value_color
