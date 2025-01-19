import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ...utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component


_stf_type = "ava.armature.humanoid"
_blender_property_name = "stf_ava_armature_humanoid"


class AVA_Armature_Humanoid(STF_BlenderComponentBase):
	mappings: bpy.props.StringProperty(name="Mappings") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_BlenderComponentModule, parent_application_object: any, component: AVA_Armature_Humanoid):
	layout.prop(component, "mappings")


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	component.mappings = json_resource.get("mappings")

	return component, context


def _stf_export(context: STF_RootExportContext, application_object: AVA_Armature_Humanoid, parent_application_object: any) -> tuple[dict, str, any]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"mappings": application_object.mappings
	}
	return ret, application_object.stf_id, context


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

