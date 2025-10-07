import bpy
import json

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module_data import STF_BlenderDataModule, STF_BlenderDataResourceBase, STF_Data_Ref
from ...utils.data_resource_utils import add_resource, export_data_resource_base, get_components_from_data_resource, import_data_resource_base
from ...utils.blender_grr.blender_grr import BlenderGRR
from .json_fallback_buffer import STF_FallbackBuffer
from .json_fallback_ui import draw_fallback


_blender_property_name = "stf_json_fallback_data"


class JsonFallbackData(STF_BlenderDataResourceBase):
	json: bpy.props.StringProperty(name="Raw Json") # type: ignore
	referenced_resources: bpy.props.CollectionProperty(type=BlenderGRR, name="Referenced Resources", options=set()) # type: ignore
	active_referenced_resource: bpy.props.IntProperty() # type: ignore
	buffers: bpy.props.CollectionProperty(type=STF_FallbackBuffer, name="Buffers", options=set()) # type: ignore
	active_buffer: bpy.props.IntProperty() # type: ignore


def _draw_resource(layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_Data_Ref, context_object: bpy.types.Collection, resource: JsonFallbackData):
	draw_fallback(layout, resource_ref, resource)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Collection) -> any:
	resource_ref, resource = add_resource(context_object, _blender_property_name, stf_id, json_resource["type"])
	import_data_resource_base(resource, json_resource)

	resource.json = json.dumps(json_resource)

	#resource.referenced_resources = json_resource.get("referenced_resources")
	#resource.buffers = json_resource.get("referenced_buffers")

	return resource


def _stf_export(context: STF_ExportContext, resource: JsonFallbackData, context_object: any) -> tuple[dict, str]:
	try:
		json_resource = json.loads(resource.json)
		if("type" not in json_resource or not json_resource["type"]):
			return None
		ret = export_data_resource_base(context, json_resource["type"], resource)
		ret = ret | json_resource
		return ret, resource.stf_id
	except:
		return None


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
