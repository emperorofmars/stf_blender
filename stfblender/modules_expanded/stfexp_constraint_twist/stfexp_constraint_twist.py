import re
import bpy
from typing import Callable

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ...utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component


_stf_type = "stfexp.constraint.twist"
_blender_property_name = "stfexp_constraint_twist"


class STFEXP_Constraint_Twist(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5) # type: ignore
	target_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Target Object") # type: ignore
	target_bone: bpy.props.StringProperty(name="Target Bone") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist):
	layout.prop(component, "weight")
	layout.prop(component, "target_object")
	if(component.target_object and type(component.target_object.data) == bpy.types.Armature):
		layout.prop_search(component, "target_bone", component.target_object.data, "bones")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	component.weight = json_resource.get("weight")
	return component


def _stf_export(context: STF_ExportContext, application_object: STFEXP_Constraint_Twist, context_object: any) -> tuple[dict, str]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"weight": application_object.weight
	}
	return ret, application_object.stf_id


def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^stfexp_constraint_twist\[(?P<component_index>[\d]+)\].weight", data_path)):
		component = application_object.stfexp_constraint_twist[int(match.groupdict()["component_index"])]
		for component_ref in application_object.stf_components:
			if(component_ref.stf_id == component.stf_id):
				return [application_object.stf_id, "components", component.stf_id, "weight"], None, None
		for component_ref in application_object.stf_instance.stf_components:
			if(component_ref.stf_id == component.stf_id):
				return [application_object.stf_id, "instance", component_ref.node_id, "components", component.stf_id, "weight"], None, None
		# TODO animation_placeholders in instances.
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[int, any], any]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "weight":
			for component_index, component in enumerate(application_object.stfexp_constraint_twist):
				if(component.stf_id == blender_object.stf_id):
					break
			return None, 0, "OBJECT", "stfexp_constraint_twist[" + str(component_index) + "].weight", 0, None
	return None


class STF_Module_STFEXP_Constraint_Twist(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["constraint.rotation", "constraint"]
	understood_application_types = [STFEXP_Constraint_Twist]
	import_func = _stf_import
	export_func = _stf_export

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["stfexp_constraint_twist"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_STFEXP_Constraint_Twist
]


def register():
	bpy.types.Object.stfexp_constraint_twist = bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist) # type: ignore
	bpy.types.Bone.stfexp_constraint_twist = bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stfexp_constraint_twist"):
		del bpy.types.Object.stfexp_constraint_twist
	if hasattr(bpy.types.Bone, "stfexp_constraint_twist"):
		del bpy.types.Bone.stfexp_constraint_twist

