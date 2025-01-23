import bpy

from .....libstf.stf_export_context import STF_ResourceExportContext
from .....libstf.stf_import_context import STF_ResourceImportContext
from ..stf_material_definition import STF_Blender_Material_Value_Module_Base, STF_Material_Value_Base


class STF_Material_Value_Color(STF_Material_Value_Base):
	color: bpy.props.FloatVectorProperty(name="Color") # type: ignore


def _value_import_func(context: STF_ResourceImportContext, json_resource: dict, material: bpy.types.Material):
	pass


def _value_export_func(context: STF_ResourceExportContext, material: bpy.types.Material) -> dict:
	pass


class STF_Blender_Material_Value_Module_Color(STF_Blender_Material_Value_Module_Base):
	property_name = "stf_material_value_color"
	value_import_func = _value_import_func
	value_export_func = _value_export_func


def register():
	bpy.types.Material.stf_material_value_color = bpy.props.CollectionProperty(type=STF_Material_Value_Color, name="Color Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_material_value_color"):
		del bpy.types.Material.stf_material_value_color
