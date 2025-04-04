import uuid
import bpy
import re
from typing import Callable

from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils import trs_utils
from ...utils.animation_conversion_utils import *


_stf_type = "stf.instance.armature"


def _translate_property_to_stf_func(application_object: bpy.types.Object, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	match = re.search(r"^pose.bones\[\"(?P<bone_name>[\w]+)\"\].location", data_path)
	if(match and "bone_name" in match.groupdict()):
		bone = application_object.data.bones[match.groupdict()["bone_name"]]
		return [application_object.stf_id, "instance", bone.stf_id, "t", translate_translation_property_to_stf(data_index)], get_translation_to_stf_translation_func(data_index)

	match = re.search(r"^pose.bones\[\"(?P<bone_name>[\w]+)\"\].rotation_quaternion", data_path)
	if(match and "bone_name" in match.groupdict()):
		bone = application_object.data.bones[match.groupdict()["bone_name"]]
		return [application_object.stf_id, "instance", bone.stf_id, "r", translate_rotation_property_to_stf(data_index)], get_rotation_to_stf_translation_func(data_index)

	match = re.search(r"^pose.bones\[\"(?P<bone_name>[\w]+)\"\].scale", data_path)
	if(match and "bone_name" in match.groupdict()):
		bone = application_object.data.bones[match.groupdict()["bone_name"]]
		return [application_object.stf_id, "instance", bone.stf_id, "s", translate_scale_property_to_stf(data_index)], get_scale_to_stf_translation_func(data_index)

	return None


def _translate_property_to_blender_func(application_object: bpy.types.Object, stf_property: str) -> tuple[str, int, Callable[[any], any]]:

	return stf_property, 0, None



def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_armature = context.import_resource(json_resource["armature"])
	if(not blender_armature or type(blender_armature) is not bpy.types.Armature):
		context.report(STFReport("Failed to import armature: " + str(json_resource.get("instance", {}).get("armature")), STFReportSeverity.Error, stf_id, _stf_type, context_object))

	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_armature)
	bpy.context.scene.collection.objects.link(blender_object)
	context.register_imported_resource(stf_id, blender_object)

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
					bone_id = blender_armature.bones[pose.name].stf_id
					if(pose.parent):
						pose.matrix = pose.parent.matrix @ trs_utils.stf_to_blender_matrix(json_resource["pose"][bone_id])
					else:
						pose.matrix = trs_utils.stf_to_blender_matrix(json_resource["pose"][bone_id])
					next_poses += pose.children
		else:
			context.report(STFReport("Failed to import pose for armature: " + str(json_resource.get("armature")), STFReportSeverity.Error, stf_id, _stf_type, blender_armature))

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and type(application_object[1]) == bpy.types.Armature):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_armature: bpy.types.Armature = application_object[1]
	ret = {"type": _stf_type}

	ret["armature"] = context.serialize_resource(blender_armature, module_kind="data")

	if(blender_object.pose):
		stf_pose: dict[str, list[list[float]]] = {}
		for blender_pose in blender_object.pose.bones:
			if blender_pose.parent:
				t, r, s = (blender_pose.parent.matrix.inverted_safe() @ blender_pose.matrix).decompose()
			else:
				t, r, s = blender_pose.matrix.decompose()
			stf_pose[blender_armature.bones[blender_pose.name].stf_id] = trs_utils.blender_to_trs(t, r, s)
		ret["pose"] = stf_pose

	return ret, str(uuid.uuid4())


def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	if(match := re.search(r"^pose.bones\[\"(?P<bone_name>[\w]+)\"\]", data_path)):
		bone = application_object.data.bones[match.groupdict()["bone_name"]]
		module_ret = context.resolve_application_property_path(bone, application_object_property_index, data_path[match.span()[1] :], data_index)
		if(module_ret):
			stf_path, translate_func = module_ret
			return [application_object.stf_id, "instance"] + stf_path, translate_func

	return None


class STF_Module_STF_Instance_Armature(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["instance.armature", "instance"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["pose.bones"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func


register_stf_modules = [
	STF_Module_STF_Instance_Armature
]


def register():
	pass

def unregister():
	pass
