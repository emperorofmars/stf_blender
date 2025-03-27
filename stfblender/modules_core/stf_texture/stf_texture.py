import bpy

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ...utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.texture"
_blender_property_name = "stf_texture"


class STF_Texture(STF_BlenderComponentBase):
	"""Define information on how an image is to be uploaded to the GPU"""
	width: bpy.props.IntProperty(name="Width", default=1024, min=1) # type: ignore
	height: bpy.props.IntProperty(name="Height", default=1024, min=1) # type: ignore
	downscale_priority: bpy.props.IntProperty(name="Downscale Priority", default=0, min=-1) # type: ignore
	# TODO much more


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_BlenderComponentModule, parent_application_object: any, component: STF_Texture):
	layout.prop(component, "width")
	layout.prop(component, "height")
	layout.prop(component, "downscale_priority")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, stf_id, _stf_type)

	component.width = json_resource.get("width", 1024)
	component.height = json_resource.get("height", 1024)
	component.downscale_priority = json_resource.get("downscale_priority", 0)

	return component


def _stf_export(context: STF_ExportContext, application_object: STF_Texture, parent_application_object: any) -> tuple[dict, str]:
	ensure_stf_id(context, application_object)
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"width": application_object.width,
		"height": application_object.height,
		"downscale_priority": application_object.downscale_priority,
	}
	return ret, application_object.stf_id


class STF_Module_STF_Texture(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [STF_Texture]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Image]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_STF_Texture
]


def register():
	bpy.types.Image.stf_texture = bpy.props.CollectionProperty(type=STF_Texture) # type: ignore

def unregister():
	if hasattr(bpy.types.Image, "stf_texture"):
		del bpy.types.Image.stf_texture
