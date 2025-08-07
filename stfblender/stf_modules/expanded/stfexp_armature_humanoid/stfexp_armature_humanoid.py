import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base


_stf_type = "stfexp.armature.humanoid"
_blender_property_name = "stfexp_armature_humanoid"


class STFEXP_Armature_Humanoid(STF_BlenderComponentBase):
	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: STFEXP_Armature_Humanoid):
	layout.prop(component, "locomotion_type")
	layout.prop(component, "no_jaw")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	component.locomotion_type = json_resource.get("locomotion_type", "planti")
	component.no_jaw = json_resource.get("no_jaw", False)

	return component


def _stf_export(context: STF_ExportContext, application_object: STFEXP_Armature_Humanoid, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)
	ret["locomotion_type"] = application_object.locomotion_type
	ret["no_jaw"] = application_object.no_jaw
	return ret, application_object.stf_id


class STF_Module_STFEXP_Armature_Humanoid(STF_BlenderComponentModule):
	"""Declares that this Armature is humanoid. Must satisfy the conditions in for the Unity humanoid rig / the VRM humanoid rig"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = []
	understood_application_types = [STFEXP_Armature_Humanoid]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_STFEXP_Armature_Humanoid
]


def register():
	bpy.types.Armature.stfexp_armature_humanoid = bpy.props.CollectionProperty(type=STFEXP_Armature_Humanoid) # type: ignore

def unregister():
	if hasattr(bpy.types.Armature, "stfexp_armature_humanoid"):
		del bpy.types.Armature.stfexp_armature_humanoid

