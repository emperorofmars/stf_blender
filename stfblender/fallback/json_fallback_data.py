import bpy
import json

from ..exporter.stf_export_context import STF_ExportContext
from ..importer.stf_import_context import STF_ImportContext
from ..base.stf_module_data import STF_BlenderDataModule, STF_BlenderDataResourceBase, STF_Data_Ref
from .json_fallback_properties import _fallback_data_blender_property_name
from ..utils.data_resource_utils import get_components_from_data_resource


_blender_property_name = _fallback_data_blender_property_name


class JsonFallbackData(STF_BlenderDataResourceBase):
	json: bpy.props.StringProperty(name="Raw Json") # type: ignore
	#referenced_resources:
	#referenced_buffers:


def _draw_resource(layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_Data_Ref, context_object: bpy.types.Collection, resource: JsonFallbackData):
	col = layout.column(align=True)
	col.label(text="Json Data:", icon="PASTEDOWN")

	json_error = False
	try:
		json.loads(resource.json)
	except:
		json_error = True
	col.alert = json_error
	col.prop(resource, "json", text="", icon="ERROR" if json_error else "NONE")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	"""fallback.stf_type = json_resource["type"]
	fallback.json = json.dumps(json_resource)
	return fallback"""
	pass


def _stf_export(context: STF_ExportContext, resource: JsonFallbackData, context_object: any) -> tuple[dict, str]:
	return json.loads(resource.json), resource.stf_id, context


class STF_Module_JsonFallbackData(STF_BlenderDataModule):
	stf_type = None
	stf_kind = "data"
	understood_application_types = [JsonFallbackData]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	draw_resource_func = _draw_resource
	get_components_func = get_components_from_data_resource


register_stf_modules = [
	STF_Module_JsonFallbackData
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=JsonFallbackData, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
