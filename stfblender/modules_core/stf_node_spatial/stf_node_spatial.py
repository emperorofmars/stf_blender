import bpy

from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_object_to_trs
from ..stf_prefab.stf_prefab import STF_BlenderNodeExportContext


_stf_type = "stf.node.spatial"


def _stf_import(context: STF_RootImportContext, json: dict, id: str, parent_application_object: any = None) -> any:
	pass


def _stf_export(context: STF_BlenderNodeExportContext, application_object: any, parent_application_object: any = None) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ensure_stf_id(blender_object)

	children = []
	for child in blender_object.children:
		children.append(context.serialize_resource(child))

	node = {
		"type": _stf_type,
		"name": blender_object.name,
		"trs": blender_object_to_trs(blender_object),
		"children": children
	}

	if(blender_object.hide_render):
		node["enabled"] = False

	# TODO: handle: blender_object.parent_type
	"""if(blender_object.parent):
		def set_parent():
			node["parent"] = context.serialize_resource(blender_object.parent)
		context.add_task(set_parent)"""
	return node, blender_object.stf_id, context


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
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index
