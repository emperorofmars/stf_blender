import json
import bpy

from ..base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ..exporter.stf_export_context import STF_ExportContext
from ..importer.stf_import_context import STF_ImportContext
from ..utils.component_utils import add_component


_blender_property_name = "stf_json_fallback_component"


class JsonFallbackComponent(STF_BlenderComponentBase):
	stf_type: bpy.props.StringProperty(name="STF Type") # type: ignore
	json: bpy.props.StringProperty(name="Raw Json") # type: ignore
	#referenced_resources:
	#referenced_buffers:


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: JsonFallbackComponent):
	layout.prop(component, "json")
	#layout.prop(component, "referenced_resources")
	#layout.prop(component, "referenced_buffers")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, json_resource["type"])

	component.stf_type = json_resource["type"]
	component.json = json.dumps(json_resource)

	#component.referenced_resources = json_resource.get("referenced_resources")
	#component.referenced_buffers = json_resource.get("referenced_buffers")

	return component


def _stf_export(context: STF_ExportContext, component: JsonFallbackComponent, context_object: any) -> tuple[dict, str]:
	return json.loads(component.json), component.stf_id, context


class STF_Module_JsonFallbackComponent(STF_BlenderComponentModule):
	stf_type = None
	stf_kind = "component"
	understood_application_types = [JsonFallbackComponent]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = None
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_JsonFallbackComponent
]


def register():
	# todo register whereever components are allowed
	pass

def unregister():
	pass