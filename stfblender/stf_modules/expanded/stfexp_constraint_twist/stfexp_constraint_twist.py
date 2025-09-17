import re
import bpy
from typing import Callable

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base
from ....utils.armature_bone import ArmatureBone
from ....utils.reference_helper import export_resource
from ....utils.animation_conversion_utils import get_component_stf_path


_stf_type = "stfexp.constraint.twist"
_blender_property_name = "stfexp_constraint_twist"


class STFEXP_Constraint_Twist(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5) # type: ignore
	target_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Target Object") # type: ignore
	target_bone: bpy.props.StringProperty(name="Target Bone") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist):
	layout.prop(component, "weight")
	if(type(context_object) == bpy.types.Bone):
		layout.prop_search(component, "target_bone", context_object.id_data, "bones", text="Target")
	else:
		layout.prop(component, "target_object")
		if(component.target_object and type(component.target_object.data) == bpy.types.Armature):
			layout.prop_search(component, "target_bone", component.target_object.data, "bones")


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	component.weight = json_resource.get("weight")

	if("target" in json_resource):
		armature = context_object.id_data
		bone_name = context_object.name
		component_id = component_ref.stf_id

		# let _get_component() -> STFEXP_Constraint_Twist
		if(type(context_object) == bpy.types.Bone):
			# Between bone-edit and object mode, references get destroyed, so we have to find the bone by name. Because Blender -.-
			def _get_component() -> STFEXP_Constraint_Twist:
				for constraint in armature.bones[bone_name].stfexp_constraint_twist:
					if(constraint.stf_id == component_id):
						return constraint
		else:
			def _get_component() -> STFEXP_Constraint_Twist:
				return component

		if(len(json_resource["target"]) == 1 and type(context_object) == bpy.types.Bone):
			def _handle_target_bone():
				for bone in armature.bones:
					if(bone.stf_info.stf_id == json_resource["target"][0]):
						constraint = _get_component()
						constraint.target_bone = bone.name
						break
			context.add_task(_handle_target_bone)
		elif(len(json_resource["target"]) == 1):
			def _handle_target_object():
				constraint = _get_component()
				constraint.target_object = context.get_imported_resource(json_resource["target"][0])
			context.add_task(_handle_target_object)
		elif(len(json_resource["target"]) == 3):
			def _handle_target_object():
				constraint = _get_component()
				constraint.target_object = context.get_imported_resource(json_resource["target"][0])
			context.add_task(_handle_target_object)
			def _handle_target_bone():
				constraint = _get_component()
				constraint.target_bone = context.get_imported_resource(json_resource["target"][2]).name
			context.add_task(_handle_target_bone)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Constraint_Twist, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["weight"] = component.weight

	def _handle():
		if(type(context_object) == ArmatureBone):
			if((context_object.armature == component.target_object or not component.target_object) and component.target_bone):
				ret["target"] = [export_resource(ret, context_object.armature.bones[component.target_bone].stf_info.stf_id)]
		elif(component.target_object):
			if(type(component.target_object.data) == bpy.types.Armature and component.target_bone):
				ret["target"] = [export_resource(ret, component.target_object.stf_info.stf_id), "instance", export_resource(ret, component.target_object.data.bones[component.target_bone].stf_info.stf_id)]
			else:
				ret["target"] = [export_resource(ret, component.target_object.stf_info.stf_id)]
	context.add_task(_handle)

	return ret, component.stf_id


"""Bone instance handling"""

def _draw_component_instance(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist):
	layout.prop(component, "weight")
	layout.prop(component, "target_object")
	if(component.target_object and type(component.target_object.data) == bpy.types.Armature):
		layout.prop_search(component, "target_bone", component.target_object.data, "bones")


def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Twist, standin_component: STFEXP_Constraint_Twist):
	standin_component.weight = component.weight
	standin_component.target_object = context_object
	standin_component.target_bone = component.target_bone


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Twist, context_object: any) -> dict:
	ret = {"weight": standin_component.weight }
	if(standin_component.target_object):
		if(type(standin_component.target_object.data) == bpy.types.Armature and standin_component.target_bone):
			ret["target"] = [export_resource(ret, standin_component.target_object.stf_info.stf_id), "instance", export_resource(ret, standin_component.target_object.data.bones[standin_component.target_bone].stf_info.stf_id)]
		else:
			ret["target"] = [export_resource(ret, standin_component.target_object.stf_info.stf_id)]
	return ret

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Twist, context_object: any):
	if("weight" in json_resource): standin_component.weight = json_resource["weight"]
	if("target" in json_resource):
		if(len(json_resource["target"]) > 0):
			def _handle_target_bone():
				standin_component.target_object = context.get_imported_resource(json_resource["target"][0])
				if(standin_component.target_object and type(standin_component.target_object.data) == bpy.types.Armature):
					standin_component.target_bone = context.get_imported_resource(json_resource["target"][2]).name
			context.add_task(_handle_target_bone)


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
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
