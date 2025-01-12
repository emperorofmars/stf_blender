import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.node_spatial_base import export_node_spatial_base, import_node_spatial_base
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.id_binding_resolver import STF_Blender_BindingResolver


_stf_type = "stf.instance.armature"


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_armature_object = context.import_resource(json_resource["armature"])
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_armature_object)

	if(not blender_armature_object or type(blender_armature_object) is not bpy.types.Armature):
		context.report(STFReport("Failed to import armature: " + str(json_resource.get("armature")), STFReportSeverity.Error, id, _stf_type, parent_application_object))

	blender_object.stf_id = id
	blender_object.stf_name = json_resource.get("name", "")

	return import_node_spatial_base(context, json_resource, id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object and type(application_object.data) == bpy.types.Armature):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object

	blender_armature: bpy.types.Armature = application_object

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_data_name if blender_object.stf_data_name else blender_object.name,
	}
	armature_context = STF_ResourceExportContext(context, ret, blender_object)

	ret["armature"] = armature_context.serialize_resource(blender_armature, blender_object.data)

	return export_node_spatial_base(context, blender_object, parent_application_object, ret)


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
