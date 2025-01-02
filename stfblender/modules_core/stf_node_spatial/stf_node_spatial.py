import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_processor import STF_Processor
from ...utils.component_utils import STF_Component
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import to_trs
from ..stf_prefab.stf_prefab import STF_BlenderNodeExportContext


_stf_type = "stf.node.spatial"


def _stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass


def _stf_export(context: STF_BlenderNodeExportContext, object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = object
	ensure_stf_id(blender_object)

	children = []
	for child in blender_object.children:
		children.append(context.serialize_resource(child))

	node = {
		"type": _stf_type,
		"name": blender_object.name,
		"trs": to_trs(blender_object.location, blender_object.rotation_quaternion, blender_object.scale),
		"children": children
	}

	# TODO: handle: blender_object.parent_type
	"""if(blender_object.parent):
		def set_parent():
			node["parent"] = context.serialize_resource(blender_object.parent)
		context.add_task(set_parent)"""
	return node, blender_object.stf_id, context


class STF_Module_STF_Node_Spatial(STF_Processor):
	stf_type = _stf_type
	stf_kind = "node"
	understood_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export


register_stf_processors = [
	STF_Module_STF_Node_Spatial
]


def register():
	bpy.types.Object.stf_id = bpy.props.StringProperty(name="Node ID") # type: ignore
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index
