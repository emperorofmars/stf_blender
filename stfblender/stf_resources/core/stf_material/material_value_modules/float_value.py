import bpy
from typing import Any

from ......stf_blender_common.base import STFPropertyPathPart, BlenderPropertyPathPart
from ......stf_blender_common.protocols import PSTF_ExportContext, PSTF_ImportContext
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Float(STF_Material_Value_Base):
	number: bpy.props.FloatProperty(name="Float") # type: ignore


def _value_import_func(context: PSTF_ImportContext, json_material: dict, blender_material: bpy.types.Material, json_resource: Any, value: STF_Material_Value_Float):
	value.number = json_resource


def _value_export_func(context: PSTF_ExportContext, json_material: dict, blender_material: bpy.types.Material, value: STF_Material_Value_Float) -> Any:
	return value.number


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Float):
	layout.prop(value, "number")


def _resolve_property_path_to_stf_func(context: PSTF_ExportContext, blender_property_path: str, value: STF_Material_Value_Float) -> STFPropertyPathPart | None:
	return STFPropertyPathPart(["number"])

def _resolve_stf_property_to_blender_func(context: PSTF_ImportContext, stf_path: list[str]) -> BlenderPropertyPathPart | None:
	return BlenderPropertyPathPart("MATERIAL", "number")


class STF_Material_Value_Module_Float(STF_Material_Value_Module_Base):
	value_type = "float"
	property_name = "stf_material_value_float"
	value_import_func = _value_import_func  # pyright: ignore[reportAssignmentType]
	value_export_func = _value_export_func  # pyright: ignore[reportAssignmentType]
	draw_func = _draw_func  # pyright: ignore[reportAssignmentType]

	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func  # pyright: ignore[reportAssignmentType]
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


def register():
	bpy.types.Material.stf_material_value_float = bpy.props.CollectionProperty(type=STF_Material_Value_Float, name="Number Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_float"):
		del bpy.types.Material.stf_material_value_float
