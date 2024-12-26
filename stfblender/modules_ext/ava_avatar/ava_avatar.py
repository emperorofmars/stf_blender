
import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_processor import STF_Processor
from ...blender_component_registry import STF_Blender_Component, STF_Component


_stf_type = "ava.avatar"


class AVA_Avatar(bpy.types.PropertyGroup):
	viewport: bpy.props.StringProperty(name="Viewport") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component: any):
	layout.label(text="WOOOOOOOO")

def _stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass

def _stf_export(context: STF_ExportContext, object: any) -> tuple[dict, str]:
	pass


class STF_Module_AVA_Avatar(STF_Blender_Component):
	stf_type = _stf_type
	stf_kind = "component"
	understood_types = [AVA_Avatar]
	import_func = _stf_import
	export_func = _stf_export
	draw_component_func = _draw_component
	filter = ["collection"]


register_stf_processors = [
	STF_Module_AVA_Avatar
]


def register():
	bpy.types.Collection.stf_ava_avatar = bpy.props.PointerProperty(type=AVA_Avatar) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_ava_avatar"):
		del bpy.types.Collection.stf_ava_avatar

