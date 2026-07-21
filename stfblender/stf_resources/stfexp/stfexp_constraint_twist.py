import bpy
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Handler_Animation, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base, preserve_component_reference
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from ....stfblender_common.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf


_stf_type = "stfexp.constraint.twist"
_blender_property_name = "stfexp_constraint_twist"


class STFEXP_Constraint_Twist(STF_ComponentResourceBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5) # type: ignore
	source: bpy.props.PointerProperty(name="Source", type=NodePathSelector) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Constraint_Twist):
	layout.use_property_split = True
	layout.prop(component, "weight")
	layout.label(text="If no Source is selected, the parent of the parent will be assumed.", icon="INFO")
	col = layout.column(align=True)
	col.use_property_split = True
	draw_node_path_selector(col, component.source, "Source")


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
	component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_resource)
	component.weight = json_resource.get("weight")

	if("source" in json_resource):
		_get_component = preserve_component_reference(component, _blender_property_name, context_resource)
		def _handle():
			component = _get_component()
			node_path_selector_from_stf(context, json_resource, json_resource["source"], component.source)
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, blender_resource: STFEXP_Constraint_Twist, context_resource: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)
	ret["weight"] = blender_resource.weight

	_get_component = preserve_component_reference(blender_resource, _blender_property_name, context_resource)
	def _handle():
		component = _get_component()
		if(source_ret := node_path_selector_to_stf(context, component.source, ret)):
			ret["source"] = source_ret
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return ret, blender_resource.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Constraint_Twist, component_instance: STFEXP_Constraint_Twist):
	component_instance.weight = component.weight
	component_instance.source.target_object = context_resource
	component_instance.source.target_bone = component.source.target_bone


def _export_component_instance(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Twist, context_object: Any) -> dict:
	ret = { "weight": standin_component.weight }
	def _handle():
		if(source_ret := node_path_selector_to_stf(context, standin_component.source, ret)):
			ret["source"] = source_ret
	context.add_task(STF_TaskSteps.DEFAULT, _handle)
	return ret

def _import_component_instance(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Twist, context_object: Any):
	if("weight" in json_resource): standin_component.weight = json_resource["weight"]
	if("source" in json_resource and len(json_resource["source"]) > 0):
		_get_component = preserve_component_reference(standin_component, _blender_property_name, context_object)
		def _handle():
			standin_component = _get_component()
			node_path_selector_from_stf(context, json_resource, json_resource["source"], standin_component.source)
		context.add_task(STF_TaskSteps.DEFAULT, _handle)


"""Animation"""

def _export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].weight", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["weight"])
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None


def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
	blender_object = context.get_imported_resource(stf_property_path[0])
	component_index = get_component_index(blender_resource, _blender_property_name, blender_object.stf_id)
	if(component_index is not None):
		match(stf_property_path[1]):
			case "weight":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].weight")
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
	return None


"""Handler definition"""

class Handler_STFEXP_Constraint_Twist(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""A rigging behaviour which copies an amount of the Y-axis rotation from the source object/bone. If no source is selected, the parent of the parent will be assumed"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["constraint.rotation", "constraint"]
	understood_blender_types = [STFEXP_Constraint_Twist]
	import_resource = _stf_import
	export_resource = _stf_export

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [_blender_property_name]
	export_blender_animation = _export_blender_animation
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw = _draw_component

	draw_instance = _draw_component # pyright: ignore[reportAssignmentType]
	update_component_instance = _set_component_instance_standin

	export_component_instance = _export_component_instance # pyright: ignore[reportAssignmentType]
	import_component_instance = _import_component_instance # pyright: ignore[reportAssignmentType]

	pretty_name_template = "Twist Constraint"


register_stf_handlers = [
	Handler_STFEXP_Constraint_Twist
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
