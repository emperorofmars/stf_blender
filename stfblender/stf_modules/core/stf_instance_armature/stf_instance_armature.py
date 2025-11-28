import bpy
import mathutils
import math
from typing import Callable

from ....base.property_path_part import STFPropertyPathPart

from .stf_instance_armature_utils import parse_standin, serialize_standin, update_armature_instance_component_standins
from ....base.stf_module import STF_Module
from ....base.stf_module_component import InstanceModComponentRef
from ....base.stf_report import STFReportSeverity, STFReport
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.id_utils import ensure_stf_id
from ....utils.animation_conversion_utils import *
from ....utils.armature_bone import ArmatureBone
from ....utils.trs_utils import close_enough


_stf_type = "stf.instance.armature"


class STF_Instance_Armature(bpy.types.PropertyGroup):
	stf_components: bpy.props.CollectionProperty(type=InstanceModComponentRef, options=set()) # type: ignore
	stf_active_component_index: bpy.props.IntProperty(options=set()) # type: ignore

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_armature = context.import_resource(json_resource["armature"], stf_kind="data")
	if(not blender_armature or type(blender_armature) is not bpy.types.Armature):
		context.report(STFReport("Failed to import armature: " + str(json_resource.get("instance", {}).get("armature")), STFReportSeverity.Error, stf_id, _stf_type, context_object))

	blender_object = bpy.data.objects.new("STF Instance", blender_armature)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]

	bpy.context.scene.collection.objects.link(blender_object)
	context.register_imported_resource(stf_id, (blender_object, blender_armature))

	if("pose" in json_resource):
		if(bpy.context.mode != "OBJECT"): bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
		bpy.context.view_layer.objects.active = blender_object
		bpy.ops.object.mode_set(mode="POSE", toggle=False)
		bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

		if(blender_object.pose):
			root_poses = []
			next_poses = [bone for bone in blender_object.pose.bones if bone.parent == None]
			while(len(next_poses) > 0):
				root_poses = next_poses; next_poses = []
				for pose in root_poses:
					bone_id = blender_armature.bones[pose.name].stf_info.stf_id

					blender_matrix = mathutils.Matrix.LocRotScale(
						mathutils.Vector((json_resource["pose"][bone_id][0][0], json_resource["pose"][bone_id][0][1], json_resource["pose"][bone_id][0][2])),
						mathutils.Quaternion((json_resource["pose"][bone_id][1][3], json_resource["pose"][bone_id][1][0], json_resource["pose"][bone_id][1][1], json_resource["pose"][bone_id][1][2])),
						mathutils.Vector((json_resource["pose"][bone_id][2][0], json_resource["pose"][bone_id][2][1], json_resource["pose"][bone_id][2][2]))
					)
					if(pose.parent):
						pose.matrix = pose.parent.matrix @ blender_matrix
					else:
						pose.matrix = mathutils.Matrix.Rotation(math.radians(90), 4, "X") @ blender_matrix
					next_poses += pose.children
		else:
			context.report(STFReport("Failed to import pose for armature: " + str(json_resource.get("armature")), STFReportSeverity.Error, stf_id, _stf_type, blender_armature))

	# components that exist on bones of this armature instance
	if("added_components" in json_resource):
		for target_id, component_ids in json_resource["added_components"].items():
			for component_id in component_ids:
				if(component := context.import_resource(component_id, blender_object, stf_kind="component")):
					for component_ref_index, component_ref in enumerate(blender_object.stf_info.stf_components):
						if(component_ref.stf_id == component_id):
							instance_component_ref = blender_object.stf_instance_armature.stf_components.add()
							instance_component_ref.stf_id = component_id
							instance_component_ref.stf_type = component_ref.stf_type
							instance_component_ref.blender_property_name = component_ref.blender_property_name
							instance_component_ref.bone = context.get_imported_resource(target_id).name
							blender_object.stf_info.stf_components.remove(component_ref_index)
							break

	# changes to bone component values for this armature instance only
	update_armature_instance_component_standins(bpy.context, blender_object)
	if("modified_components" in json_resource):
		for component_id, standin_component_json in json_resource["modified_components"].items():
			parse_standin(context, blender_object, component_id, standin_component_json)

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and type(application_object[1]) == bpy.types.Armature):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_armature: bpy.types.Armature = application_object[1]

	ensure_stf_id(context, blender_object.stf_instance)
	ret = {"type": _stf_type, "name": blender_object.stf_instance.stf_name}

	ret["armature"] = context.serialize_resource(blender_armature, module_kind="data")

	if(blender_object.pose):
		stf_pose: dict[str, list[list[float]]] = {}
		for blender_pose in blender_object.pose.bones:
			# let t, r, s
			if blender_pose.parent:
				t, r, s = (blender_pose.parent.matrix.inverted_safe() @ blender_pose.matrix).decompose()
			else:
				t, r, s = (mathutils.Matrix.Rotation(math.radians(-90), 4, "X") @ blender_pose.matrix).decompose()

			# already in armature space, so no trs_utils conversion
			stf_pose[blender_armature.bones[blender_pose.name].stf_info.stf_id] = [
				[close_enough(t[0]), close_enough(t[1]), close_enough(t[2])],
				[close_enough(r[1]), close_enough(r[2]), close_enough(r[3]), close_enough(r[0], 1)],
				[close_enough(s[0], 1), close_enough(s[1], 1), close_enough(s[2], 1)]
			]
		ret["pose"] = stf_pose

	# components that exist on bones of this armature instance
	if(len(blender_object.stf_instance_armature.stf_components) > 0):
		added_components = {}
		for component_ref in blender_object.stf_instance_armature.stf_components:
			components = getattr(blender_object, component_ref.blender_property_name)
			for component in components:
				if(component.stf_id == component_ref.stf_id):
					component_id = context.serialize_resource(component, None, module_kind="component")
					if(component_id):
						bone = blender_armature.bones[component_ref.bone]
						if(bone.stf_info.stf_id not in added_components):
							added_components[bone.stf_info.stf_id] = []
						added_components[bone.stf_info.stf_id].append(component_id)
		ret["added_components"] = added_components

	# changes to bone component values for this armature instance only
	if(len(blender_object.stf_instance_armature_component_standins.stf_components) > 0):
		modified_components = {}
		for component_ref in blender_object.stf_instance_armature_component_standins.stf_components:
			if(component_ref.override):
				#bone = blender_armature.bones[component_ref.bone]
				standin_override = serialize_standin(context, blender_object, component_ref)
				if(standin_override):
					modified_components[component_ref.stf_id] = standin_override
			if(len(modified_components) > 0):
				ret["modified_components"] = modified_components

	return ret, blender_object.stf_instance.stf_id


def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	import re
	if(match := re.search(r"^pose.bones\[\"(?P<bone_name>[\w. -:,]+)\"\]", data_path)):
		return STFPropertyPathPart([application_object.stf_info.stf_id, "instance"]) + context.resolve_application_property_path(ArmatureBone(application_object.data, match.groupdict()["bone_name"]), application_object_property_index, data_path[match.span()[1] :])
	return None

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	return context.resolve_stf_property_path(stf_path[1:], application_object)


class STF_Module_STF_Instance_Armature(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["instance.armature", "instance"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = None

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["pose.bones"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Instance_Armature
]


def register():
	bpy.types.Object.stf_instance_armature = bpy.props.PointerProperty(type=STF_Instance_Armature)
	bpy.types.Object.stf_instance_armature_component_standins = bpy.props.PointerProperty(type=STF_Instance_Armature)

def unregister():
	if hasattr(bpy.types.Object, "stf_instance_armature"):
		del bpy.types.Object.stf_instance_armature
	if hasattr(bpy.types.Object, "stf_instance_armature_component_standins"):
		del bpy.types.Object.stf_instance_armature_component_standins
