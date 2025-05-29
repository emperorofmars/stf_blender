import bpy

from ...libstf.stf_export_context import STF_ExportContext
from ...libstf.stf_import_context import STF_ImportContext
from ..utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component


_stf_type = "ava.armature.humanoid"
_blender_property_name = "stf_ava_armature_humanoid"


class AVA_Armature_Humanoid(STF_BlenderComponentBase):
	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_Armature_Humanoid):
	layout.prop(component, "locomotion_type")
	layout.prop(component, "no_jaw")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	component.locomotion_type = json_resource.get("locomotion_type", "planti")
	component.no_jaw = json_resource.get("no_jaw", False)

	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Armature_Humanoid, parent_application_object: any) -> tuple[dict, str]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"locomotion_type": application_object.locomotion_type,
		"no_jaw": application_object.no_jaw
	}
	return ret, application_object.stf_id


class STF_Module_AVA_Armature_Humanoid(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = []
	understood_application_types = [AVA_Armature_Humanoid]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_Armature_Humanoid
]


def register():
	bpy.types.Armature.stf_ava_armature_humanoid = bpy.props.CollectionProperty(type=AVA_Armature_Humanoid) # type: ignore

def unregister():
	if hasattr(bpy.types.Armature, "stf_ava_armature_humanoid"):
		del bpy.types.Armature.stf_ava_armature_humanoid

