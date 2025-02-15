import bpy
import re
from typing import Callable
import mathutils

from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ....libstf.stf_export_context import STF_ResourceExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext
from ..stf_node.node_base import export_node_base, import_node_base
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.id_binding_resolver import STF_Blender_BindingResolver
from ...utils import trs_utils


_stf_type = "stf.instance.armature"


def __get_rotation_to_stf_translation_func(index: int) -> Callable[[any], any]:
	def __func(value: float) -> float:
		match(index):
			case 0: return value
			case 1: return value
			case 2: return -value
			case 3: return value
	return __func


def __translate_rotation_property_to_stf(index: int) -> str:
	match(index):
			case 0: return "x"
			case 1: return "z"
			case 2: return "y"
			case 3: return "w"
	return None


def _translate_property_to_stf_func(blender_object: bpy.types.Object, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	match = re.search(r"^pose.bones\[\"(?P<bone_name>[\w]+)\"\].rotation_quaternion", data_path)
	if(match and "bone_name" in match.groupdict()):
		bone = blender_object.data.bones[match.groupdict()["bone_name"]]
		return [bone.stf_id, "r", __translate_rotation_property_to_stf(data_index)], __get_rotation_to_stf_translation_func(data_index)
	return [], None


def _translate_property_to_blender_func(blender_object: bpy.types.Object, stf_property: str) -> tuple[str, int, Callable[[any], any]]:
	return stf_property, 0, None



def _stf_import(context: STF_ResourceImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_armature = context.import_resource(json_resource["instance"]["armature"])
	if(not blender_armature or type(blender_armature) is not bpy.types.Armature):
		context.report(STFReport("Failed to import armature: " + str(json_resource.get("instance", {}).get("armature")), STFReportSeverity.Error, stf_id, _stf_type, parent_application_object))

	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_armature)
	bpy.context.scene.collection.objects.link(blender_object)
	context.register_imported_resource(stf_id, blender_object)

	if("pose" in json_resource["instance"]):
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
						pose.matrix = pose.parent.matrix @ trs_utils.stf_to_blender_matrix(json_resource["instance"]["pose"][bone_id])
					else:
						pose.matrix = trs_utils.stf_to_blender_matrix(json_resource["instance"]["pose"][bone_id])
					next_poses += pose.children
		else:
			context.report(STFReport("Failed to import pose for armature: " + str(json_resource.get("instance", {}).get("armature")), STFReportSeverity.Error, stf_id, _stf_type, blender_armature))

	return import_node_base(context, json_resource, stf_id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object and type(application_object.data) == bpy.types.Armature):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ret = {"type": _stf_type}
	ret, stf_id, context = export_node_base(context, blender_object, parent_application_object, ret)

	ret_instance = {}
	ret["instance"] = ret_instance

	blender_armature: bpy.types.Armature = application_object.data
	armature_instance_context = STF_ResourceExportContext(context, ret, blender_object)

	ret_instance["armature"] = armature_instance_context.serialize_resource(blender_armature)

	if(blender_object.pose):
		stf_pose: dict[str, list[list[float]]] = {}
		for blender_pose in blender_object.pose.bones:
			if blender_pose.parent:
				t, r, s = (blender_pose.parent.matrix.inverted_safe() @ blender_pose.matrix).decompose()
			else:
				t, r, s = blender_pose.matrix.decompose()
			stf_pose[blender_armature.bones[blender_pose.name].stf_id] = trs_utils.blender_to_trs(t, r, s)
		ret_instance["pose"] = stf_pose

	return export_node_base(context, application_object, parent_application_object, ret)


def _resolve_id_binding_func(blender_object: any, stf_id: str) -> any:
	return blender_object.data if blender_object.stf_data_id == stf_id else None


class STF_Module_STF_Instance_Armature(STF_Module, STF_Blender_BindingResolver):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["instance.armature", "instance.prefab", "instance", "stf.node", "node"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	target_blender_binding_types = [bpy.types.Object]
	resolve_id_binding_func = _resolve_id_binding_func

	translate_property_to_stf_func = _translate_property_to_stf_func
	translate_property_to_blender_func: _translate_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Instance_Armature
]


def register():
	pass

def unregister():
	pass
