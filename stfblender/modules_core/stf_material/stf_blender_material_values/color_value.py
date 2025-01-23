import bpy

from ..stf_material_definition import STF_Blender_Material_Value_Module_Base, STF_Material_Value_Base


class STF_Material_Value_Color(STF_Material_Value_Base):
	color: bpy.props.FloatVectorProperty(name="Color") # type: ignore


class STF_Blender_Material_Value_Module_Color(STF_Blender_Material_Value_Module_Base):
	property_name: str = "stf_material_value_color"
	multi_value: bool = True


def register():
	bpy.types.Material.stf_material_value_color = bpy.props.CollectionProperty(type=STF_Material_Value_Color, name="Color Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_color"):
		del bpy.types.Material.stf_material_value_color
