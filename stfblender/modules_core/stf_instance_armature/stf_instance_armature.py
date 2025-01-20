import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ..stf_prefab.stf_prefab import STF_BlenderNodeExportContext, STF_BlenderNodeImportContext
from ..stf_node_spatial.node_spatial_base import export_node_spatial_base, import_node_spatial_base
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.id_binding_resolver import STF_Blender_BindingResolver
from ...utils import trs_utils


_stf_type = "stf.instance.armature"


def _stf_import(context: STF_BlenderNodeImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_armature_object = context.import_resource(json_resource["armature"])
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_armature_object)

	if(not blender_armature_object or type(blender_armature_object) is not bpy.types.Armature):
		context.report(STFReport("Failed to import armature: " + str(json_resource.get("armature")), STFReportSeverity.Error, stf_id, _stf_type, parent_application_object))

	blender_object.stf_id = stf_id
	blender_object.stf_name = json_resource.get("name", "")

	def _set_poses():
		if("pose" in json_resource and blender_object.pose):
			root_poses = []
			next_poses = [bone for bone in blender_object.pose.bones if bone.parent == None]
			while(len(next_poses) > 0):
				root_poses = next_poses; next_poses = []
				for pose in root_poses:
					bone_id = blender_armature_object.bones[pose.name].stf_id
					if(pose.parent):
						pose.matrix = pose.parent.matrix @ trs_utils.stf_to_blender_matrix(json_resource["pose"][bone_id])
					else:
						pose.matrix = trs_utils.stf_to_blender_matrix(json_resource["pose"][bone_id])
					next_poses += pose.children
	context.add_task(_set_poses)

	return import_node_spatial_base(context, json_resource, stf_id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object and type(application_object.data) == bpy.types.Armature):
		return 1000
	else:
		return -1

def _stf_export(context: STF_BlenderNodeExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ensure_stf_id(context, blender_object)
	ret = {
		"type": _stf_type,
	}

	blender_armature: bpy.types.Armature = application_object.data
	armature_instance_context = STF_ResourceExportContext(context, ret, blender_object)

	ret["armature"] = armature_instance_context.serialize_resource(blender_armature, blender_object)

	if(blender_object.pose):
		stf_pose: dict[str, list[list[float]]] = {}
		for blender_pose in blender_object.pose.bones:
			if blender_pose.parent:
				t, r, s = (blender_pose.parent.matrix.inverted_safe() @ blender_pose.matrix).decompose()
			else:
				t, r, s = blender_pose.matrix.decompose()
			stf_pose[blender_armature.bones[blender_pose.name].stf_id] = trs_utils.blender_to_trs(t, r, s)
		ret["pose"] = stf_pose

	return export_node_spatial_base(context, application_object, parent_application_object, ret)


def _resolve_id_binding_func(blender_object: any, id: str) -> any:
	return blender_object.data if blender_object.stf_data_id == id else None


class STF_Module_STF_Instance_Armature(STF_Module, STF_Blender_BindingResolver):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["instance.armature", "instance.prefab", "instance"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	target_blender_binding_types = [bpy.types.Object]
	resolve_id_binding_func = _resolve_id_binding_func


register_stf_modules = [
	STF_Module_STF_Instance_Armature
]


def register():
	pass

def unregister():
	pass
