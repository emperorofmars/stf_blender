import json
import bpy

from ..exporter.stf_export_context import STF_ExportContext
from ..importer.stf_import_context import STF_ImportContext
from ..core.stf_module import STF_Module


class JsonFallbackData(bpy.types.PropertyGroup):
	stf_type: bpy.props.StringProperty(name="STF Type") # type: ignore
	json: bpy.props.StringProperty(name="Raw Json") # type: ignore
	#referenced_resources:
	#referenced_buffers:


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	"""fallback.stf_type = json_resource["type"]
	fallback.json = json.dumps(json_resource)
	return fallback"""
	pass


def _stf_export(context: STF_ExportContext, resource: JsonFallbackData, context_object: any) -> tuple[dict, str]:
	return json.loads(resource.json), resource.stf_id, context


class STF_Module_JsonFallbackData(STF_Module):
	stf_type = None
	stf_kind = "data"
	understood_application_types = [JsonFallbackData]
	import_func = _stf_import
	export_func = _stf_export


register_stf_modules = [
	STF_Module_JsonFallbackData
]


def register():
	# todo register on COllection
	pass

def unregister():
	pass