import bpy
import re
from typing import Callable

from ....libstf.stf_module import STF_Module
from .node_base import export_node_base, import_node_base
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ....libstf.stf_import_context import STF_ResourceImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext
from .node_base_properties_conversion import stf_node_base_translate_property_to_stf_func, stf_node_base_translate_property_to_blender_func


_stf_type = "stf.node"


def _stf_import(context: STF_ResourceImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)
	context.register_imported_resource(stf_id, blender_object)
	return import_node_base(context, json_resource, stf_id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object):
		if(not application_object.instance_collection and not application_object.data):
			return 1000
		else:
			return 0
	else:
		return -1

def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	ret = {"type": _stf_type}
	return export_node_base(context, application_object, parent_application_object, ret)


class STF_Module_STF_Node(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["node", "node.spatial"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	translate_property_to_stf_func = stf_node_base_translate_property_to_stf_func
	translate_property_to_blender_func: stf_node_base_translate_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Node
]


def register():
	bpy.types.Object.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Object.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Object.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_name"):
		del bpy.types.Object.stf_name
	if hasattr(bpy.types.Object, "stf_name_source_of_truth"):
		del bpy.types.Object.stf_name_source_of_truth
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index
