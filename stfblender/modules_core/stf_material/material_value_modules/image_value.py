import bpy

from .....libstf.stf_export_context import STF_ExportContext
from .....libstf.stf_import_context import STF_ImportContext
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Image(STF_Material_Value_Base):
	image: bpy.props.PointerProperty(type=bpy.types.Texture, name="Image") # type: ignore
	# uv_multiplier:
	# uv_offset:


def _value_import_func(context: STF_ImportContext, blender_material: bpy.types.Material, json_resource: any, value: STF_Material_Value_Image):
	if("image" in json_resource):
		value.image = context.import_resource(json_resource["image"], stf_kind="data")


def _value_export_func(context: STF_ExportContext, blender_material: bpy.types.Material, value: STF_Material_Value_Image) -> any:
	ret = {}
	if(value.image): ret["image"] = context.serialize_resource(value.image)
	return ret


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Image):
	layout.prop(value, "image")


class STF_Material_Value_Module_Image(STF_Material_Value_Module_Base):
	value_type = "image"
	property_name = "stf_material_value_image"
	value_import_func = _value_import_func
	value_export_func = _value_export_func
	draw_func = _draw_func


def register():
	bpy.types.Material.stf_material_value_image = bpy.props.CollectionProperty(type=STF_Material_Value_Image, name="Image Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_image"):
		del bpy.types.Material.stf_material_value_image
