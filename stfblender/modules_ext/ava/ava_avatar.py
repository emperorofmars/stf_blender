import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ...utils.component_utils import STF_Blender_Component, add_component


_stf_type = "ava.avatar"
_blender_property_name = "stf_ava_avatar"


class AVA_Avatar(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="Name") # type: ignore

	automap: bpy.props.BoolProperty(name="Automap", default=True) # type: ignore
	viewport: bpy.props.PointerProperty(type=bpy.types.Object, name="Viewport") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Blender_Component, parent_application_object: any, component: AVA_Avatar):
	layout.prop(component, "automap")
	layout.prop(component, "viewport")


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> tuple[any, any]:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	component.automap = json_resource.get("automap")

	return component, context


def _stf_export(context: STF_RootExportContext, application_object: AVA_Avatar, parent_application_object: any) -> tuple[dict, str, any]:
	ret = {
		"type": _stf_type,
		"name": "",
		"automap": application_object.automap
	}
	return ret, application_object.stf_id, context


class STF_Module_AVA_Avatar(STF_Blender_Component):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_Avatar]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_Avatar
]


def register():
	bpy.types.Collection.stf_ava_avatar = bpy.props.CollectionProperty(type=AVA_Avatar) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_ava_avatar"):
		del bpy.types.Collection.stf_ava_avatar

