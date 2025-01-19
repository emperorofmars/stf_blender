import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ...utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component


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


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	component.width = json_resource.get("width", 1024)
	component.height = json_resource.get("height", 1024)
	component.downscale_priority = json_resource.get("downscale_priority", 0)

	return component, context


def _stf_export(context: STF_RootExportContext, application_object: STF_Texture, parent_application_object: any) -> tuple[dict, str, any]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"width": application_object.width,
		"height": application_object.height,
		"downscale_priority": application_object.downscale_priority,
	}
	return ret, application_object.stf_id, context


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
