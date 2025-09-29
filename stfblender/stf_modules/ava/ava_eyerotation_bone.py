import bpy

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "ava.eye_rotation.bone"
_blender_property_name = "ava_eye_rotation_bone"


class AVA_EyeRotation_Bone(STF_BlenderComponentBase):
	limit_up: bpy.props.FloatProperty(name="Up", default=15, options=set()) # type: ignore
	limit_down: bpy.props.FloatProperty(name="Down", default=12, options=set()) # type: ignore
	limit_in: bpy.props.FloatProperty(name="In", default=15, options=set()) # type: ignore
	limit_out: bpy.props.FloatProperty(name="Out", default=16, options=set()) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_EyeRotation_Bone):
	layout.use_property_split = True
	col = layout.column(align=True)
	col.prop(component, "limit_up")
	col.prop(component, "limit_down")
	col.prop(component, "limit_in")
	col.prop(component, "limit_out")



def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	component.limit_up = json_resource.get("up", 15)
	component.limit_down = json_resource.get("down", 12)
	component.limit_in = json_resource.get("in", 15)
	component.limit_out = json_resource.get("out", 16)

	return component


def _stf_export(context: STF_ExportContext, component: AVA_EyeRotation_Bone, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["up"] = component.limit_up
	ret["down"] = component.limit_down
	ret["in"] = component.limit_in
	ret["out"] = component.limit_out
	return ret, component.stf_id


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
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=AVA_EyeRotation_Bone, options=set()))

def unregister():
	if hasattr(bpy.types.Armature, _blender_property_name):
		delattr(bpy.types.Armature, _blender_property_name)

