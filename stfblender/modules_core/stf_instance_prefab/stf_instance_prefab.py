import bpy


from ....libstf.stf_export_context import STF_ResourceExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.node_spatial_base import export_node_spatial_base, import_node_spatial_base
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.instance.prefab"


# NOTE this 'works', but doing this in a proper manner would be a bit more involved, since Blender's 'Collection Instance' feature is very meh and mostly pointless.
# This is not part of the MVP. The code is here, but not visible to the STF_Registry.


def _stf_import(context: STF_ResourceImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_collection = context.import_resource(json_resource["prefab"])

	if(not blender_collection or type(blender_collection) is not bpy.types.Collection):
		context.report(STFReport("Failed to import prefab: " + str(json_resource.get("prefab")), STFReportSeverity.Error, id, _stf_type, parent_application_object))

	blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)
	blender_object.stf_id = id
	blender_object.stf_name = json_resource.get("name", "")

	blender_object.instance_type = "COLLECTION"
	blender_object.instance_collection = blender_collection

	# TODO handle prefab instance modifications

	return import_node_spatial_base(context, json_resource, id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object and application_object.instance_type == "COLLECTION" and application_object.instance_collection):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ensure_stf_id(context, blender_object)

	ret = { "type": _stf_type, }
	prefab_context = STF_ResourceExportContext(context, ret, application_object)
	ret["prefab"] = prefab_context.serialize_resource(blender_object.instance_collection)

	# TODO prefab instance modifications

	return export_node_spatial_base(context, blender_object, parent_application_object, ret)


class STF_Module_STF_Instance_Prefab(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["instance.prefab", "instance"]
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
