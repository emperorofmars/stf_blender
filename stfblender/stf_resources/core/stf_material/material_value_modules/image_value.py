import bpy
from typing import Any

from ......stf_blender_common.base import STFPropertyPathPart, BlenderPropertyPathPart, STF_Category
from ......stf_blender_common.protocols import PSTF_ExportContext, PSTF_ImportContext
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Image(STF_Material_Value_Base):
	image: bpy.props.PointerProperty(type=bpy.types.Image, name="Image") # type: ignore
	# uv_multiplier:
	# uv_offset:


def _value_import_func(context: PSTF_ImportContext, json_material: dict, blender_material: bpy.types.Material, json_resource: Any, value: STF_Material_Value_Image):
	if("image" in json_resource and json_resource["image"] != None):
		value.image = context.import_resource(json_material, json_resource["image"], stf_category=STF_Category.DATA)


def _value_export_func(context: PSTF_ExportContext, json_material: dict, blender_material: bpy.types.Material, value: STF_Material_Value_Image) -> Any:
	ret = {}
	if(value.image):
		ret["image"] = context.serialize_resource(json_material, value.image, stf_category=STF_Category.DATA)
	return ret


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Image):
	layout.prop(value, "image")


def _resolve_property_path_to_stf_func(context: PSTF_ExportContext, blender_property_path: str, value: STF_Material_Value_Image) -> STFPropertyPathPart | None:
	return None

def _resolve_stf_property_to_blender_func(context: PSTF_ImportContext, stf_path: list[str]) -> BlenderPropertyPathPart | None:
	return None


class STF_Material_Value_Module_Image(STF_Material_Value_Module_Base):
	value_type = "image"
	property_name = "stf_material_value_image"
	value_import_func = _value_import_func # pyright: ignore[reportAssignmentType]
	value_export_func = _value_export_func # pyright: ignore[reportAssignmentType]
	draw_func = _draw_func # pyright: ignore[reportAssignmentType]

	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func # pyright: ignore[reportAssignmentType]
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func # pyright: ignore[reportAssignmentType]


def register():
	bpy.types.Material.stf_material_value_image = bpy.props.CollectionProperty(type=STF_Material_Value_Image, name="Image Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_image"):
		del bpy.types.Material.stf_material_value_image
