import bpy

from ..stf_material_definition import STF_Material_Value_Base


class STF_Material_Value_Texture(STF_Material_Value_Base):
	texture: bpy.props.PointerProperty(type=bpy.types.Texture, name="Texture") # type: ignore
	# texture_type:
	# uv_multiplier:
	# uv_offset:


def register():
	bpy.types.Material.stf_material_value_texture = bpy.props.CollectionProperty(type=STF_Material_Value_Texture, name="Texture Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_texture"):
		del bpy.types.Material.stf_material_value_texture
