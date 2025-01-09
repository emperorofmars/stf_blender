import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_ExportHook, STF_ImportHook
from ....libstf.stf_report import STF_Report_Severity, STFReport
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_object_data_id


_stf_type = "stf.instance.armature"


def _hook_can_handle_stf_object_func(json_resource: dict) -> tuple[bool, dict, str]:
	for id, component in json_resource.get("components", {}).items():
		# TODO also check 'likeness'
		if(component.get("type") == _stf_type):
			return (True, component, id)
	return (False, None, None)

def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> tuple[any, any]:
	blender_armature = context.import_resource(json_resource["armature"])

	if(not blender_armature or type(blender_armature) is not bpy.types.Collection):
		context.report(STFReport("Failed to import armature: " + str(json_resource.get("armature")), STF_Report_Severity.Error, id, _stf_type, parent_application_object))

	blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_armature)
	blender_object.stf_data_id = id
	blender_object.stf_data_name = json_resource.get("name", "")

	return blender_object, context


def _hook_can_handle_application_object_func(application_object: any) -> tuple[bool, any]:
	if(type(application_object.data) == bpy.types.Armature):
		return (True, application_object.data)
	else:
		return (False, None)

def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	parent_blender_object: bpy.types.Object = parent_application_object
	ensure_stf_object_data_id(parent_blender_object)

	blender_armature: bpy.types.Armature = application_object
	armature_id = context.serialize_resource(blender_armature)

	ret = {
		"type": _stf_type,
		"name": parent_blender_object.stf_data_name if parent_blender_object.stf_data_name else parent_blender_object.name,
		"armature": armature_id,
	}

	return ret, parent_blender_object.stf_data_id, context


class STF_Module_STF_Instance_Armature(STF_ImportHook, STF_ExportHook):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["instance.armature", "instance.prefab", "instance"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object

	hook_target_stf_type = "stf.node.spatial"
	hook_can_handle_stf_object_func = _hook_can_handle_stf_object_func

	hook_target_application_types = [bpy.types.Object]
	hook_can_handle_application_object_func = _hook_can_handle_application_object_func


register_stf_modules = [
	STF_Module_STF_Instance_Armature
]


def register():
	pass

def unregister():
	pass
