import bpy
import json

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module_data import STF_BlenderDataModule, STF_BlenderDataResourceBase, STF_Data_Ref
from ...utils.data_resource_utils import add_resource, export_data_resource_base, get_components_from_data_resource, import_data_resource_base
from ...utils.reference_helper import register_exported_buffer, register_exported_resource
from ...base.blender_grr import BlenderGRR, construct_blender_grr, resolve_blender_grr
from .json_fallback_buffer import STF_FallbackBuffer, decode_buffer, encode_buffer
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
	resource: JsonFallbackData = resource
	import_data_resource_base(resource, json_resource)

	resource.json = json.dumps(json_resource)

	def _handle():
		for resource_id in json_resource.get("referenced_resources", []):
			resource_grr = resource.referenced_resources.add()
			if(referenced_resource := context.import_resource(resource_id)):
				construct_blender_grr(referenced_resource, resource_grr, resource_id)
	context.add_task(_handle)
	
	for buffer_id in json_resource.get("referenced_buffers", []):
		encode_buffer(context, buffer_id, resource)

	return resource


def _stf_export(context: STF_ExportContext, resource: JsonFallbackData, context_object: any) -> tuple[dict, str]:
	try:
		json_resource = json.loads(resource.json)
		if("type" not in json_resource or not json_resource["type"]):
			return None
		ret = export_data_resource_base(context, json_resource["type"], resource)
		ret = ret | json_resource

		ret["referenced_resources"] = []
		ret["referenced_buffers"] = []

		for referenced_resource in resource.referenced_resources:
			referenced_resource: BlenderGRR = referenced_resource
			if(blender_resource := resolve_blender_grr(referenced_resource)):
				def _handle():
					register_exported_resource(ret, context.serialize_resource(blender_resource))
				context.add_task(_handle)
		
		for buffer in resource.buffers:
			register_exported_buffer(ret, decode_buffer(context, buffer))

		return ret, resource.stf_id
	except:
		return None


class STF_Module_JsonFallbackData(STF_BlenderDataModule):
	"""This type is not supported.
	You have to edit the raw json string, resource references and base64 encoded binary buffers"""
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
