import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_ExportHook, STF_ImportHook
from ....libstf.stf_report import STF_Report_Severity, STFReport
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_object_data_id


_stf_type = "stf.instance.prefab"


def _hook_can_handle_stf_object_func(json_resource: dict) -> tuple[bool, dict, str]:
	for id, component in json_resource.get("components", {}).items():
		# TODO also check 'likeness'
		if(component.get("type") == "stf.instance.prefab"):
			return (True, component, id)
	return (False, None, None)

def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> any:
	pass


def _hook_can_handle_application_object_func(application_object: any) -> tuple[bool, any]:
	if(application_object.instance_collection):
		return (True, application_object.instance_collection)
	else:
		return (False, None)

def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	parent_blender_object: bpy.types.Object = parent_application_object
	ensure_stf_object_data_id(parent_blender_object)

	prefab_id = context.serialize_resource(application_object)

	ret = {
		"type": _stf_type,
		"name": parent_blender_object.stf_data_name if parent_blender_object.stf_data_name else parent_blender_object.name,
		"prefab": prefab_id,
		# TODO prefab instance modifications
	}

	return ret, parent_blender_object.stf_data_id, context


class STF_Module_STF_Instance_Prefab(STF_ImportHook, STF_ExportHook):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["instance.prefab", "instance"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object

	hook_target_stf_type = "stf.node.spatial"
	hook_can_handle_stf_object_func = _hook_can_handle_stf_object_func

	hook_target_application_types = [bpy.types.Object]
	hook_can_handle_application_object_func = _hook_can_handle_application_object_func


register_stf_modules = [
	STF_Module_STF_Instance_Prefab
]


def register():
	pass

def unregister():
	pass
