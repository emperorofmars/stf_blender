import bpy

from ...importer.stf_import_context import STF_ImportContext
from ...exporter.stf_export_context import STF_ExportContext
from ...core.stf_report import STFReportSeverity
from ...core.stf_module import STF_Module
from ...utils.boilerplate import boilerplate_register, boilerplate_unregister
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.prefab"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	collection = bpy.data.collections.new(json_resource.get("name", context.get_filename()))
	collection.stf_id = stf_id
	if(json_resource.get("name")):
		collection.stf_name = json_resource["name"]
		collection.stf_name_source_of_truth = True
	bpy.context.scene.collection.children.link(collection)
	collection.stf_use_collection_as_prefab = True

	for node_id in json_resource.get("root_nodes", []):
		context.import_resource(node_id, context_object=collection, stf_kind="node")

	for animation_id in json_resource.get("animations", []):
		context.import_resource(animation_id, context_object=collection, stf_kind="data")

	return collection


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	collection: bpy.types.Collection = application_object
	ensure_stf_id(context, collection)

	root_nodes = []
	animations = []
	ret = {
		"type": _stf_type,
		"name": collection.stf_name if collection.stf_name_source_of_truth else collection.name,
		"root_nodes": root_nodes,
		"animations": animations,
	}

	for blender_object in collection.all_objects[:]:
		if(type(blender_object) is bpy.types.Object and blender_object.parent == None):
			root_nodes.append(context.serialize_resource(blender_object, module_kind="node", context_object=collection))

	for action in bpy.data.actions:
		if(stf_animation_id := context.serialize_resource(action, module_kind="data", context_object=collection, export_fail_severity=STFReportSeverity.Debug)):
			animations.append(stf_animation_id)

	return ret, collection.stf_id


class STF_Module_STF_Prefab(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["prefab"]
	understood_application_types = [bpy.types.Collection]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Prefab
]

def register():
	boilerplate_register(bpy.types.Collection, "data")
	bpy.types.Collection.stf_use_collection_as_prefab = bpy.props.BoolProperty(name="Use As STF Prefab", default=False)

def unregister():
	boilerplate_unregister(bpy.types.Collection, "data")
	if hasattr(bpy.types.Collection, "stf_use_collection_as_prefab"):
		del bpy.types.Collection.stf_use_collection_as_prefab
