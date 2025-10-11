import re
import bpy
from typing import Callable

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ...utils.animation_conversion_utils import get_component_stf_path
from ...base.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf


_stf_type = "stfexp.constraint.twist"
_blender_property_name = "stfexp_constraint_twist"


class STFEXP_Constraint_Twist(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5) # type: ignore
	target: bpy.props.PointerProperty(name="Target", type=NodePathSelector) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist):
	layout.use_property_split = True
	layout.prop(component, "weight")
	layout.label(text="If no target is selected, the parent of the parent will be assumed.", icon="INFO")
	col = layout.column(align=True)
	col.use_property_split = True
	draw_node_path_selector(col, component.target)


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, context_object)
	component.weight = json_resource.get("weight")

	if("target" in json_resource):
		_get_component = preserve_component_reference(component, context_object)
		def _handle():
			component = _get_component()
			node_path_selector_from_stf(context, json_resource, json_resource["target"], component.target)
		context.add_task(_handle)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Constraint_Twist, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["weight"] = component.weight

	_get_component = preserve_component_reference(component, context_object)
	def _handle():
		component = _get_component()
		if(target_ret := node_path_selector_to_stf(context, component.target, ret)):
			ret["target"] = target_ret
	context.add_task(_handle)

	return ret, component.stf_id


"""Bone instance handling"""

def _draw_component_instance(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist):
	layout.use_property_split = True
	layout.prop(component, "weight")
	layout.label(text="If no target is selected, the parent of the parent will be assumed.", icon="INFO")

	col = layout.column(align=True)
	col.use_property_split = True
	draw_node_path_selector(col, component.target)


def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist, standin_component: STFEXP_Constraint_Twist):
	standin_component.weight = component.weight
	standin_component.target.target_object = context_object
	standin_component.target.target_bone = component.target.target_bone 


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Twist, context_object: any) -> dict:
	ret = { "weight": standin_component.weight }
	def _handle():
		if(target_ret := node_path_selector_to_stf(context, standin_component.target, ret)):
			ret["target"] = target_ret
	context.add_task(_handle)
	return ret

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Twist, context_object: any):
	if("weight" in json_resource): standin_component.weight = json_resource["weight"]
	if("target" in json_resource and len(json_resource["target"]) > 0):
		_get_component = preserve_component_reference(standin_component, context_object)
		def _handle():
			standin_component = _get_component()
			node_path_selector_from_stf(context, json_resource, json_resource["target"], standin_component.target)
		context.add_task(_handle)


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^stfexp_constraint_twist\[(?P<component_index>[\d]+)\].weight", data_path)):
		component = application_object.stfexp_constraint_twist[int(match.groupdict()["component_index"])]
		component_path = get_component_stf_path(application_object, component)
		if(component_path):
			return component_path + ["weight"], None, None
	if(match := re.search(r"^stfexp_constraint_twist\[(?P<component_index>[\d]+)\].enabled", data_path)):
		component = application_object.stfexp_constraint_twist[int(match.groupdict()["component_index"])]
		component_path = get_component_stf_path(application_object, component)
		if(component_path):
			return component_path + ["enabled"], None, None
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	# let component_index
	for component_index, component in enumerate(application_object.stfexp_constraint_twist):
		if(component.stf_id == blender_object.stf_id):
			break
	match(stf_path[1]):
		case "weight":
			return None, 0, "OBJECT", "stfexp_constraint_twist[" + str(component_index) + "].weight", 0, None
		case "enabled":
			return None, 0, "OBJECT", "stfexp_constraint_twist[" + str(component_index) + "].enabled", 0, None
	return None


class STF_Module_STFEXP_Constraint_Twist(STF_BlenderComponentModule):
	"""A rigging behaviour which copies an amount of the Y-axis rotation from the target object/bone. If no target is selected, the parent of the parent will be assumed"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["constraint.rotation", "constraint"]
	understood_application_types = [STFEXP_Constraint_Twist]
	import_func = _stf_import
	export_func = _stf_export

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = [_blender_property_name]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	draw_component_instance_func = _draw_component_instance
	set_component_instance_standin_func = _set_component_instance_standin

	serialize_component_instance_standin_func = _serialize_component_instance_standin_func
	parse_component_instance_standin_func = _parse_component_instance_standin_func


register_stf_modules = [
	STF_Module_STFEXP_Constraint_Twist
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
