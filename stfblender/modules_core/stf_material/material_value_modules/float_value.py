import bpy

from .....libstf.stf_export_context import STF_ResourceExportContext
from .....libstf.stf_import_context import STF_ResourceImportContext
from ..stf_material_definition import STF_Material_Value_Base, STF_Material_Value_Module_Base


class STF_Material_Value_Float(STF_Material_Value_Base):
	number: bpy.props.FloatProperty(name="Float") # type: ignore


def _value_import_func(context: STF_ResourceImportContext, blender_material: bpy.types.Material, json_resource: any, value: STF_Material_Value_Float):
	value.number = json_resource


def _value_export_func(context: STF_ResourceExportContext, blender_material: bpy.types.Material, value: STF_Material_Value_Float) -> any:
	return value.number


def _draw_func(layout: bpy.types.UILayout, context: bpy.types.Context, blender_material: bpy.types.Material, value: STF_Material_Value_Float):
	layout.prop(value, "number")


class STF_Material_Value_Module_Float(STF_Material_Value_Module_Base):
	value_type = "float"
	property_name = "stf_material_value_float"
	value_import_func = _value_import_func
	value_export_func = _value_export_func
	draw_func = _draw_func


def register():
	bpy.types.Material.stf_material_value_float = bpy.props.CollectionProperty(type=STF_Material_Value_Float, name="Number Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_float"):
		del bpy.types.Material.stf_material_value_float
