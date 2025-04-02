import re
import bpy
from typing import Callable

from ...libstf.stf_export_context import STF_ExportContext
from ...libstf.stf_import_context import STF_ImportContext
from ..utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component


_stf_type = "ava.constraint.twist"
_blender_property_name = "stf_ava_constraint_twist"


class AVA_Constraint_Twist(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_BlenderComponentModule, context_object: any, component: AVA_Constraint_Twist):
	layout.prop(component, "weight")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	component.weight = json_resource.get("weight")
	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Constraint_Twist, context_object: any) -> tuple[dict, str]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"weight": application_object.weight
	}
	return ret, application_object.stf_id


def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	if(match := re.search(r"^stf_ava_constraint_twist\[(?P<component_index>[\d]+)\].weight", data_path)):
		component = application_object.stf_ava_constraint_twist[int(match.groupdict()["component_index"])]
		return [application_object.stf_id, "components", component.stf_id, "weight"], None
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, int, Callable[[any], any]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "weight":
			for component_index, component in enumerate(application_object.stf_ava_constraint_twist):
				if(component.stf_id == blender_object.stf_id):
					break
			return None, 0, "OBJECT", "stf_ava_constraint_twist[" + str(component_index) + "].weight", 0, None
	return None


class STF_Module_AVA_Constraint_Twist(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["constraint.rotation", "constraint"]
	understood_application_types = [AVA_Constraint_Twist]
	import_func = _stf_import
	export_func = _stf_export

	understood_application_property_path_types = [bpy.types.Object, bpy.types.Bone]
	understood_application_property_path_parts = ["stf_ava_constraint_twist"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

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

