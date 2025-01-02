import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_processor import STF_Processor
from ...utils.component_utils import STF_Blender_Component


_stf_type = "ava.avatar"


class AVA_Avatar(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	viewport: bpy.props.StringProperty(name="Viewport") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Blender_Component, object: any, component: AVA_Avatar):
	layout.prop(component, "viewport")


def _stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass

def _stf_export(context: any, object: any) -> tuple[dict, str, any]:
	pass


class STF_Module_AVA_Avatar(STF_Blender_Component, STF_Processor):
	stf_type = _stf_type
	stf_kind = "component"
	understood_types = [AVA_Avatar]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = "stf_ava_avatar"
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component


register_stf_processors = [
	STF_Module_AVA_Avatar
]


def register():
	bpy.types.Collection.stf_ava_avatar = bpy.props.CollectionProperty(type=AVA_Avatar) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_ava_avatar"):
		del bpy.types.Collection.stf_ava_avatar

