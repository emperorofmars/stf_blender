import bpy

from ..stf_material_definition import STF_Material_Value_Base


class STF_Material_Value_RawJson(STF_Material_Value_Base):
	json_text: bpy.props.StringProperty(name="Raw Json Text") # type: ignore
	# todo references to blender objects


def register():
	bpy.types.Material.stf_material_value_raw_json = bpy.props.CollectionProperty(type=STF_Material_Value_RawJson, name="Raw Json Value")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_raw_json"):
		del bpy.types.Material.stf_material_value_raw_json
