import bpy

from ....base.stf_module import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "ava.eye_rotation.bone"
_blender_property_name = "ava_eye_rotation_bone"


class AVA_EyeRotation_Bone(STF_BlenderComponentBase):
	limit_up: bpy.props.FloatProperty(name="Up", default=15) # type: ignore
	limit_down: bpy.props.FloatProperty(name="Down", default=12) # type: ignore
	limit_in: bpy.props.FloatProperty(name="In", default=15) # type: ignore
	limit_out: bpy.props.FloatProperty(name="Out", default=16) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_EyeRotation_Bone):
	layout.prop(component, "limit_up")
	layout.prop(component, "limit_down")
	layout.prop(component, "limit_in")
	layout.prop(component, "limit_out")



def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	component.limit_up = json_resource.get("up", 15)
	component.limit_down = json_resource.get("down", 12)
	component.limit_in = json_resource.get("in", 15)
	component.limit_out = json_resource.get("out", 16)

	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_EyeRotation_Bone, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, application_object)
	ret["up"] = application_object.limit_up
	ret["down"] = application_object.limit_down
	ret["in"] = application_object.limit_in
	ret["out"] = application_object.limit_out
	return ret, application_object.stf_id


class STF_Module_AVA_EyeRotation_Bone(STF_BlenderComponentModule):
	"""Define limits to eyebone rotations"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_EyeRotation_Bone]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_EyeRotation_Bone
]


def register():
	bpy.types.Armature.ava_eye_rotation_bone = bpy.props.CollectionProperty(type=AVA_EyeRotation_Bone) # type: ignore

def unregister():
	if hasattr(bpy.types.Armature, "ava_eye_rotation_bone"):
		del bpy.types.Armature.ava_eye_rotation_bone

