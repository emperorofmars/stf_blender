import bpy
from typing import Callable

from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from ..stf_material_definition import STF_Material_Value_Module_Base, STF_Material_Value_Base
from .....base.property_path_part import BlenderPropertyPathPart, STFPropertyPathPart


class STF_Material_Value_Color(STF_Material_Value_Base):
	color: bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", size=4, min=0, max=1, default=(1,1,1,1)) # type: ignore


def _value_import_func(context: STF_ImportContext, blender_material: bpy.types.Material, json_resource: any, value: STF_Material_Value_Color):
	value.color = (json_resource[0],json_resource[1], json_resource[2], json_resource[3])


def _value_export_func(context: STF_ExportContext, blender_material: bpy.types.Material, value: STF_Material_Value_Color) -> any:
	return [value.color[0], value.color[1], value.color[2], value.color[3]]


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Color):
	layout.prop(value, "color")


def _resolve_property_path_to_stf_func(context: STF_ExportContext, blender_property_path: str, value: STF_Material_Value_Color) -> STFPropertyPathPart:
	return STFPropertyPathPart(["color"])

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str]) -> BlenderPropertyPathPart:
	return BlenderPropertyPathPart("MATERIAL", "color")


class STF_Material_Value_Module_Color(STF_Material_Value_Module_Base):
	value_type = "color"
	property_name = "stf_material_value_color"
	value_import_func = _value_import_func
	value_export_func = _value_export_func
	draw_func = _draw_func

	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


def register():
	bpy.types.Material.stf_material_value_color = bpy.props.CollectionProperty(type=STF_Material_Value_Color, name="Color Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_color"):
		del bpy.types.Material.stf_material_value_color
