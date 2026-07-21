import bpy
from typing import Any

from ......stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Float(STF_Material_Value_Base):
	number: bpy.props.FloatProperty(name="Float") # type: ignore


def _import_material_value(context: STF_ImportContext, json_material: dict, blender_material: bpy.types.Material, json_resource: Any, value: STF_Material_Value_Float):
	value.number = json_resource


def _export_material_value(context: STF_ExportContext, json_material: dict, blender_material: bpy.types.Material, value: STF_Material_Value_Float) -> Any:
	return value.number


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Float):
	layout.prop(value, "number")


def _export_blender_animation(context: STF_ExportContext, blender_property_path: str, value: STF_Material_Value_Float) -> STFPropertyPathPart | None:
	return STFPropertyPathPart(["number"])

def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_path: list[str]) -> BlenderPropertyPathPart | None:
	return BlenderPropertyPathPart("MATERIAL", "number")


class STF_Material_Value_Module_Float(STF_Material_Value_Module_Base):
	value_type = "float"
	property_name = "stf_material_value_float"
	import_material_value = _import_material_value  # pyright: ignore[reportAssignmentType]
	export_material_value = _export_material_value  # pyright: ignore[reportAssignmentType]
	draw_func = _draw_func  # pyright: ignore[reportAssignmentType]

	export_blender_animation = _export_blender_animation  # pyright: ignore[reportAssignmentType]
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func


def register():
	bpy.types.Material.stf_material_value_float = bpy.props.CollectionProperty(type=STF_Material_Value_Float, name="Number Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_float"):
		del bpy.types.Material.stf_material_value_float
