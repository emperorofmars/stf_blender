import json
import bpy

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ...utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component


_blender_property_name = "stf_json_fallback_component"


class JsonFallbackComponent(STF_BlenderComponentBase):
	"""Define information on how an image is to be uploaded to the GPU"""
	stf_type: bpy.props.StringProperty(name="STF Type") # type: ignore
	json: bpy.props.StringProperty(name="Raw Json") # type: ignore
	#referenced_resources:
	#referenced_buffers:


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_BlenderComponentModule, parent_application_object: any, component: JsonFallbackComponent):
	layout.prop(component, "json")
	#layout.prop(component, "referenced_resources")
	#layout.prop(component, "referenced_buffers")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, json_resource["type"])

	component.stf_type = json_resource["type"]
	component.json = json.dumps(json_resource)

	#component.referenced_resources = json_resource.get("referenced_resources")
	#component.referenced_buffers = json_resource.get("referenced_buffers")

	return component, context


def _stf_export(context: STF_ExportContext, application_object: JsonFallbackComponent, parent_application_object: any) -> tuple[dict, str, any]:
	ret = {
		"type": application_object.stf_type,
		"name": application_object.stf_name,
		"width": application_object.width,
		"height": application_object.height,
		"downscale_priority": application_object.downscale_priority,
	}
	return ret, application_object.stf_id, context


class STF_Module_JsonFallbackComponent(STF_BlenderComponentModule):
	stf_type = None
	stf_kind = "component"
	understood_application_types = [JsonFallbackComponent]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Image]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_JsonFallbackComponent
]


def register():
	pass

def unregister():
	pass