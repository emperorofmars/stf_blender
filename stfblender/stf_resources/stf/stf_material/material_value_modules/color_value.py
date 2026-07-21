import bpy
from typing import Any

from ......stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart
from ..stf_material_definition import STF_Material_Value_Module_Base, STF_Material_Value_Base


class STF_Material_Value_Color(STF_Material_Value_Base):
	color: bpy.props.FloatVectorProperty(name="Color", subtype="COLOR", size=4, min=0, max=1, default=(1,1,1,1)) # type: ignore


def _import_material_value(context: STF_ImportContext, json_material: dict, blender_material: bpy.types.Material, json_resource: Any, value: STF_Material_Value_Color):
	value.color = (json_resource[0],json_resource[1], json_resource[2], json_resource[3])


def _export_material_value(context: STF_ExportContext, json_material: dict, blender_material: bpy.types.Material, value: STF_Material_Value_Color) -> Any:
	return [value.color[0], value.color[1], value.color[2], value.color[3]]


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Color):
	layout.prop(value, "color")


def _export_blender_animation(context: STF_ExportContext, blender_property_path: str, value: STF_Material_Value_Color) -> STFPropertyPathPart | None:
	return STFPropertyPathPart(["color"])

def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_path: list[str]) -> BlenderPropertyPathPart | None:
	return BlenderPropertyPathPart("MATERIAL", "color")


class STF_Material_Value_Module_Color(STF_Material_Value_Module_Base):
	value_type = "color"
	property_name = "stf_material_value_color"
	import_material_value = _import_material_value  # pyright: ignore[reportAssignmentType]
	export_material_value = _export_material_value  # pyright: ignore[reportAssignmentType]
	draw_func = _draw_func  # pyright: ignore[reportAssignmentType]

	export_blender_animation = _export_blender_animation  # pyright: ignore[reportAssignmentType]
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func


def register():
	bpy.types.Material.stf_material_value_color = bpy.props.CollectionProperty(type=STF_Material_Value_Color, name="Color Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_color"):
		del bpy.types.Material.stf_material_value_color
