import bpy

from .....libstf.stf_export_context import STF_ResourceExportContext
from .....libstf.stf_import_context import STF_ResourceImportContext
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Texture(STF_Material_Value_Base):
	texture: bpy.props.PointerProperty(type=bpy.types.Texture, name="Texture") # type: ignore
	# texture_type:
	# uv_multiplier:
	# uv_offset:


def _value_import_func(context: STF_ResourceImportContext, blender_material: bpy.types.Material, json_resource: any, value: STF_Material_Value_Texture):
	if("texture" in json_resource):
		value.texture = context.import_resource(json_resource["texture"])


def _value_export_func(context: STF_ResourceExportContext, blender_material: bpy.types.Material, value: STF_Material_Value_Texture) -> any:
	ret = {}
	if(value.texture): ret["texture"] = context.serialize_resource(value.texture)
	return ret


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Texture):
	layout.prop(value, "texture")


class STF_Material_Value_Module_Texture(STF_Material_Value_Module_Base):
	value_type = "texture"
	property_name = "stf_material_value_texture"
	value_import_func = _value_import_func
	value_export_func = _value_export_func
	draw_func = _draw_func


def register():
	bpy.types.Material.stf_material_value_texture = bpy.props.CollectionProperty(type=STF_Material_Value_Texture, name="Texture Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_texture"):
		del bpy.types.Material.stf_material_value_texture
