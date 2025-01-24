import bpy

from .....libstf.stf_export_context import STF_ResourceExportContext
from .....libstf.stf_import_context import STF_ResourceImportContext
from ..stf_material_definition import STF_Blender_Material_Value_Module_Base, STF_Material_Value_Base, add_property


class STF_Material_Value_Color(STF_Material_Value_Base):
	color: bpy.props.FloatVectorProperty(name="Color") # type: ignore


def _value_import_func(context: STF_ResourceImportContext, json_resource: dict, blender_material: bpy.types.Material):
	pass


def _value_export_func(context: STF_ResourceExportContext, blender_material: bpy.types.Material, value: STF_Material_Value_Color) -> any:
	return [value.color[0], value.color[1], value.color[2]]


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Color):
	layout.prop(value, "color")


class STF_Blender_Material_Value_Module_Color(STF_Blender_Material_Value_Module_Base):
	value_type = "color"
	property_name = "stf_material_value_color"
	value_import_func = _value_import_func
	value_export_func = _value_export_func
	draw_func = _draw_func



def register():
	bpy.types.Material.stf_material_value_color = bpy.props.CollectionProperty(type=STF_Material_Value_Color, name="Color Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_color"):
		del bpy.types.Material.stf_material_value_color
