import bpy

from ...utils.node_spatial_base import export_node_spatial_base, import_node_spatial_base
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component, get_components_from_object
from ..stf_prefab.stf_prefab import STF_BlenderNodeExportContext, STF_BlenderNodeImportContext


_stf_type = "stf.node.spatial"


def _stf_import(context: STF_BlenderNodeImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)
	return import_node_spatial_base(context, json_resource, id, parent_application_object, blender_object)


def _stf_export(context: STF_BlenderNodeExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	ret = { "type": _stf_type, }
	return export_node_spatial_base(context, application_object, parent_application_object, ret)


class STF_Module_STF_Node_Spatial(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["node", "node.spatial"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Node_Spatial
]


def register():
	bpy.types.Object.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Object.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_name"):
		del bpy.types.Object.stf_name
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index
