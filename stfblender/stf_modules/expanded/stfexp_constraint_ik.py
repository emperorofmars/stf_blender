import bpy
import re
import math
from typing import Any

from ...common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_TaskSteps, STF_Category
from ...common.module_component import STF_BlenderComponentBase, STF_BlenderBoneComponentModule, STF_Component_Ref
from ...common.module_component.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ...common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from ...common.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf


_stf_type = "stfexp.constraint.ik"
_blender_property_name = "stfexp_constraint_ik"


class STFEXP_Constraint_IK(STF_BlenderComponentBase):
	chain_length: bpy.props.IntProperty(name="Chain Length", default=2, min=1, options=set()) # type: ignore
	target: bpy.props.PointerProperty(name="Target", type=NodePathSelector, options=set()) # type: ignore
	pole: bpy.props.PointerProperty(name="Pole", type=NodePathSelector, options=set()) # type: ignore


def _process_func(component: STFEXP_Constraint_IK, context_object: bpy.types.Bone, target_object: bpy.types.Object):
	pose_bone: bpy.types.PoseBone = target_object.pose.bones[context_object.name]

	index = 0
	while index < len(pose_bone.constraints):
		if(type(pose_bone.constraints[index]) == bpy.types.KinematicConstraint):
			pose_bone.constraints.remove(pose_bone.constraints[index])
			index -= 1
		index += 1

	constraint: bpy.types.KinematicConstraint = pose_bone.constraints.new("IK")
	constraint.chain_count = component.chain_length

	if(component.target.target_object):
		constraint.target = component.target.target_object
	if(component.target.target_bone):
		constraint.subtarget = component.target.target_bone
		if(not component.target.target_object):
			constraint.target = target_object

	if(component.pole.target_object):
		constraint.pole_angle = math.pi
		constraint.pole_target = component.pole.target_object
	if(component.pole.target_bone):
		constraint.pole_angle = math.pi
		constraint.pole_subtarget = component.pole.target_bone
		if(not component.pole.target_object):
			constraint.pole_target = target_object

	if(constraint.pole_target and constraint.pole_subtarget):
		# https://blender.stackexchange.com/a/19755
		# todo deal with poles from other armatures or just objects

		def signed_angle(vector_u, vector_v, normal):
			# Normal specifies orientation
			angle = vector_u.angle(vector_v)
			if vector_u.cross(vector_v).angle(normal) < 1:
				angle = -angle
			return angle

		def get_pole_angle(base_bone, ik_bone, pole_location):
			pole_normal = (ik_bone.tail - base_bone.head).cross(pole_location - base_bone.head)
			projected_pole_axis = pole_normal.cross(base_bone.tail - base_bone.head)
			return signed_angle(base_bone.x_axis, projected_pole_axis, base_bone.tail - base_bone.head)

		root_bone = pose_bone
		for _ in range(component.chain_length):
			if(root_bone and root_bone.parent):
				root_bone = root_bone.parent
		if(root_bone):
			constraint.pole_angle = get_pole_angle(root_bone, pose_bone, constraint.pole_target.pose.bones[constraint.pole_subtarget].matrix.translation)


class ParseFromCurrentArmatureInstance(bpy.types.Operator):
	bl_idname = "stf.stfexp_constraint_ik_parse_from_armature_instance"
	bl_label = "Parse from Armature Instance"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	@classmethod
	def poll(cls, context: bpy.types.Context): return context.object is not None and type(context.object.data) == bpy.types.Armature and context.bone

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event, message="This will overwrite current values!")

	def execute(self, context: bpy.types.Context):
		component: STFEXP_Constraint_IK = None
		for component in getattr(context.bone, _blender_property_name):
			if(component.stf_id == self.component_id):
				break
		else:
			return {"CANCELLED"}

		posebone = context.object.pose.bones[context.bone.name]

		constraint: bpy.types.KinematicConstraint = None
		for constraint in posebone.constraints:
			if(type(constraint) == bpy.types.KinematicConstraint):
				break
		else:
			# Nothing to do
			return {"CANCELLED"}

		component.chain_length = constraint.chain_count
		if(constraint.target and constraint.target == context.object):
			component.target.target_bone = constraint.subtarget
		else:
			component.target.target_bone = None

		if(constraint.pole_target and constraint.pole_target == context.object):
			component.pole.target_bone = constraint.pole_subtarget
		else:
			component.pole.target_bone = None
		return {"FINISHED"}


class ApplyToCurrentArmatureInstance(bpy.types.Operator):
	bl_idname = "stf.stfexp_constraint_ik_apply_to_armature_instance"
	bl_label = "Apply to Armature Instance"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	@classmethod
	def poll(cls, context: bpy.types.Context): return context.object is not None and type(context.object.data) == bpy.types.Armature and context.bone

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event, message="This will modify the PoseBone's constraints!")

	def execute(self, context: bpy.types.Context):
		component: STFEXP_Constraint_IK = None
		for component in getattr(context.bone, _blender_property_name):
			if(component.stf_id == self.component_id):
				break
		else:
			return {"CANCELLED"}

		_process_func(component, context.bone, context.object)
		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STFEXP_Constraint_IK):
	layout.use_property_split = True
	layout.prop(component, "chain_length")

	col = layout.column(align=True)
	col.use_property_split = True
	draw_node_path_selector(col, component.target, "Target")
	draw_node_path_selector(col, component.pole, "Pole")

	layout.separator()
	layout.operator(ParseFromCurrentArmatureInstance.bl_idname).component_id = component.stf_id
	layout.operator(ApplyToCurrentArmatureInstance.bl_idname).component_id = component.stf_id


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	component.chain_length = json_resource.get("chain_length")

	if("target" in json_resource or "pole" in json_resource):
		_get_component = preserve_component_reference(component, _blender_property_name, context_object)
		def _handle():
			component = _get_component()
			if("target" in json_resource):
				node_path_selector_from_stf(context, json_resource, json_resource["target"], component.target)
			if("pole" in json_resource):
				node_path_selector_from_stf(context, json_resource, json_resource["pole"], component.pole)
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Constraint_IK, context_object: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret["chain_length"] = component.chain_length

	_get_component = preserve_component_reference(component, _blender_property_name, context_object)
	def _handle():
		component = _get_component()
		if(target_ret := node_path_selector_to_stf(context, component.target, ret)):
			ret["target"] = target_ret
		if(pole_ret := node_path_selector_to_stf(context, component.pole, ret)):
			ret["pole"] = pole_ret
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return ret, component.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STFEXP_Constraint_IK, standin_component: STFEXP_Constraint_IK):
	standin_component.chain_length = component.chain_length
	standin_component.target.target_object = context_object
	standin_component.target.target_bone = component.target.target_bone
	standin_component.pole.target_object = context_object
	standin_component.pole.target_bone = component.pole.target_bone


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_IK, context_object: Any) -> dict:
	ret = { "chain_length": standin_component.chain_length }
	_get_component = preserve_component_reference(standin_component, _blender_property_name, context_object)
	def _handle():
		component = _get_component()
		if(target_ret := node_path_selector_to_stf(context, component.target, ret)):
			ret["target"] = target_ret
		if(pole_ret := node_path_selector_to_stf(context, component.pole, ret)):
			ret["pole"] = pole_ret
	context.add_task(STF_TaskSteps.DEFAULT, _handle)
	return ret

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_IK, context_object: Any):
	if("chain_length" in json_resource): standin_component.chain_length = json_resource["chain_length"]

	if("target" in json_resource or "pole" in json_resource):
		_get_component = preserve_component_reference(standin_component, _blender_property_name, context_object)
		def _handle():
			component = _get_component()
			if("target" in json_resource):
				node_path_selector_from_stf(context, json_resource, json_resource["target"], component.target)
			if("pole" in json_resource):
				node_path_selector_from_stf(context, json_resource, json_resource["pole"], component.pole)
		context.add_task(STF_TaskSteps.DEFAULT, _handle)


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: Any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: Any) -> BlenderPropertyPathPart:
	blender_object = context.get_imported_resource(stf_path[0])
	if(component_index := get_component_index(application_object, _blender_property_name, blender_object.stf_id)):
		match(stf_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
	return None


"""Module definition"""

class STF_Module_STFEXP_Constraint_IK(STF_BlenderBoneComponentModule):
	"""Inverse Kinematic Constraint"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["constraint.ik", "constraint"]
	understood_application_types = [STFEXP_Constraint_IK]
	import_func = _stf_import
	export_func = _stf_export

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = [_blender_property_name]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Bone]
	draw_component_func = _draw_component

	draw_component_instance_func = _draw_component
	set_component_instance_standin_func = _set_component_instance_standin

	serialize_component_instance_standin_func = _serialize_component_instance_standin_func
	parse_component_instance_standin_func = _parse_component_instance_standin_func

	process_func = _process_func

	pretty_name_template = "IK Constraint"


register_stf_modules = [
	STF_Module_STFEXP_Constraint_IK
]


def register():
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_IK, options=set()))
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_IK, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
