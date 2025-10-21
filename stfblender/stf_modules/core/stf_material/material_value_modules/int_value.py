import bpy
from typing import Callable

from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Int(STF_Material_Value_Base):
	number: bpy.props.IntProperty(name="Int") # type: ignore


def _value_import_func(context: STF_ImportContext, blender_material: bpy.types.Material, json_resource: any, value: STF_Material_Value_Int):
	value.number = json_resource


def _value_export_func(context: STF_ExportContext, blender_material: bpy.types.Material, value: STF_Material_Value_Int) -> any:
	return value.number


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Int):
	layout.prop(value, "number")


def _resolve_property_path_to_stf_func(context: STF_ExportContext, blender_property_path: str, value: STF_Material_Value_Int) -> tuple[list, Callable[[int, any], any], list[int]]:
	return ["number"], None, None

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str]) -> tuple[str, list[int], Callable[[list[float]], list[float]]]:
	return "number", None, None


class STF_Material_Value_Module_Int(STF_Material_Value_Module_Base):
	value_type = "int"
	property_name = "stf_material_value_int"
	value_import_func = _value_import_func
	value_export_func = _value_export_func
	draw_func = _draw_func

	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


def register():
	bpy.types.Material.stf_material_value_int = bpy.props.CollectionProperty(type=STF_Material_Value_Int, name="Number Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_int"):
		del bpy.types.Material.stf_material_value_int
