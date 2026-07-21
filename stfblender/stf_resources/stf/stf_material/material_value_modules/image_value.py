import bpy
from typing import Any

from ......stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Image(STF_Material_Value_Base):
	image: bpy.props.PointerProperty(type=bpy.types.Image, name="Image") # type: ignore
	# uv_multiplier:
	# uv_offset:


def _import_material_value(context: STF_ImportContext, json_material: dict, blender_material: bpy.types.Material, json_resource: Any, value: STF_Material_Value_Image):
	if("image" in json_resource and json_resource["image"] != None):
		value.image = context.import_resource(json_material, json_resource["image"], stf_category=STF_Category.DATA)


def _export_material_value(context: STF_ExportContext, json_material: dict, blender_material: bpy.types.Material, value: STF_Material_Value_Image) -> Any:
	ret = {}
	if(value.image):
		ret["image"] = context.serialize_resource(json_material, value.image, stf_category=STF_Category.DATA)
	return ret


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Image):
	layout.prop(value, "image")


def _export_blender_animation(context: STF_ExportContext, blender_property_path: str, value: STF_Material_Value_Image) -> STFPropertyPathPart | None:
	return None

def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_path: list[str]) -> BlenderPropertyPathPart | None:
	return None


class STF_Material_Value_Module_Image(STF_Material_Value_Module_Base):
	value_type = "image"
	property_name = "stf_material_value_image"
	import_material_value = _import_material_value # pyright: ignore[reportAssignmentType]
	export_material_value = _export_material_value # pyright: ignore[reportAssignmentType]
	draw_func = _draw_func # pyright: ignore[reportAssignmentType]

	export_blender_animation = _export_blender_animation # pyright: ignore[reportAssignmentType]
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func # pyright: ignore[reportAssignmentType]


def register():
	bpy.types.Material.stf_material_value_image = bpy.props.CollectionProperty(type=STF_Material_Value_Image, name="Image Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_image"):
		del bpy.types.Material.stf_material_value_image
