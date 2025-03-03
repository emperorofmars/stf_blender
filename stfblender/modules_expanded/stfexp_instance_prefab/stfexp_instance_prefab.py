import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...modules_core.stf_node.node_base import export_node_base, import_node_base


_stf_type = "stfexp.instance.prefab"


# NOTE this 'works', but doing this in a proper manner would be a bit more involved, since Blender's 'Collection Instance' feature is very meh and mostly pointless.
# This is not part of the MVP. The code is here, but not visible to the STF_Registry.


def _stf_import(context: STF_ResourceImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_collection = context.import_resource(json_resource["instance"]["prefab"])

	if(not blender_collection or type(blender_collection) is not bpy.types.Collection):
		context.report(STFReport("Failed to import prefab: " + str(json_resource.get("instance").get("prefab")), STFReportSeverity.Error, id, _stf_type, parent_application_object))

	blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)

	blender_object.instance_type = "COLLECTION"
	blender_object.instance_collection = blender_collection

	# TODO handle prefab instance modifications

	return import_node_base(context, json_resource, id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object and application_object.instance_type == "COLLECTION" and application_object.instance_collection):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ret = {"type": _stf_type}
	ret, stf_id, context = export_node_base(context, blender_object, parent_application_object, ret)

	ret_instance = {}
	ret["instance"] = ret_instance

	prefab_context = STF_ResourceExportContext(context, ret, application_object)
	ret_instance["prefab"] = prefab_context.serialize_resource(blender_object.instance_collection)

	# TODO prefab instance modifications

	return export_node_base(context, blender_object, parent_application_object, ret)


class STF_Module_STF_Instance_Prefab(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["instance.prefab", "instance", "stf.node", "node"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Instance_Prefab
]


def register():
	pass

def unregister():
	pass
