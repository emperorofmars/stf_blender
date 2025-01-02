import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_processor import STF_Processor
from ...utils.component_utils import STF_Component

from ..stf_node_spatial.stf_node_spatial import STF_BlenderNodeExportContext


_stf_type = "stf.prefab"
_stf_type_node = "stf.node.spatial"


def _stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass

def _stf_export(context: STF_ExportContext, object: any) -> tuple[dict, str]:
	collection: bpy.types.Collection = object
	if(not collection.stf_id):
		import uuid
		collection.stf_id = str(uuid.uuid4())

	ret = {
		"type": _stf_type,
		"name": collection.name,
		"nodes": [],
		"components": [],
		# "animations": None,
		"used_resources": [],
		"used_buffers": [],
	}

	node_export_context = STF_BlenderNodeExportContext(context, ret)
	for object in collection.all_objects:
		node_export_context.export_node(object)


	for component in collection.stf_components:
		print(component)


	return ret, collection.stf_id


class STF_Module_STF_Prefab(STF_Processor):
	stf_type = _stf_type
	stf_kind = "data"
	understood_types = [bpy.types.Collection]
	import_func = _stf_import
	export_func = _stf_export


register_stf_processors = [
	STF_Module_STF_Prefab
]


def register():
	bpy.types.Collection.stf_id = bpy.props.StringProperty(name="Prefab ID") # type: ignore
	bpy.types.Collection.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Collection.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Collection, "stf_id"):
		del bpy.types.Collection.stf_id
	if hasattr(bpy.types.Collection, "stf_components"):
		del bpy.types.Collection.stf_components
	if hasattr(bpy.types.Collection, "stf_active_component_index"):
		del bpy.types.Collection.stf_active_component_index
