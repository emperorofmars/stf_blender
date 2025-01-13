import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ...utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component


_stf_type = "ava.constraint.twist"
_blender_property_name = "stf_ava_constraint_twist"


class AVA_Constraint_Twist(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_BlenderComponentModule, parent_application_object: any, component: AVA_Constraint_Twist):
	layout.prop(component, "weight")


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	component.weight = json_resource.get("weight")

	return component, context


def _stf_export(context: STF_RootExportContext, application_object: AVA_Constraint_Twist, parent_application_object: any) -> tuple[dict, str, any]:
	ret = {
		"type": _stf_type,
		"name": "",
		"weight": application_object.weight
	}
	return ret, application_object.stf_id, context


class STF_Module_AVA_Constraint_Twist(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["constraint.rotation", "constraint"]
	understood_application_types = [AVA_Constraint_Twist]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_Constraint_Twist
]


def register():
	bpy.types.Object.stf_ava_constraint_twist = bpy.props.CollectionProperty(type=AVA_Constraint_Twist) # type: ignore
	bpy.types.Bone.stf_ava_constraint_twist = bpy.props.CollectionProperty(type=AVA_Constraint_Twist) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stf_ava_constraint_twist"):
		del bpy.types.Object.stf_ava_constraint_twist
	if hasattr(bpy.types.Bone, "stf_ava_constraint_twist"):
		del bpy.types.Bone.stf_ava_constraint_twist

