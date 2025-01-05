import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ...utils.component_utils import STF_Blender_Component


_stf_type = "ava.avatar"


class AVA_Avatar(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="Name") # type: ignore

	viewport: bpy.props.StringProperty(name="Viewport") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Blender_Component, parent_application_object: any, component: AVA_Avatar):
	layout.prop(component, "viewport")


def _stf_import(context: STF_RootImportContext, json: dict, id: str, parent_application_object: any) -> any:
	pass

def _stf_export(context: STF_RootExportContext, application_object: AVA_Avatar, parent_application_object: any = None) -> tuple[dict, str, any]:
	ret = {
		"type": _stf_type,
		"name": "",
		"viewport": application_object.viewport
	}
	return ret, application_object.stf_id, context


class STF_Module_AVA_Avatar(STF_Blender_Component):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_Avatar]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = "stf_ava_avatar"
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = []


register_stf_processors = [
	STF_Module_AVA_Avatar
]


def register():
	bpy.types.Collection.stf_ava_avatar = bpy.props.CollectionProperty(type=AVA_Avatar) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_ava_avatar"):
		del bpy.types.Collection.stf_ava_avatar

