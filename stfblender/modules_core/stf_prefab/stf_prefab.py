import bpy


from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReport
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.prefab"


def _stf_import(context: STF_RootImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	collection = bpy.data.collections.new(json_resource.get("name", context.get_filename()))
	collection.stf_id = stf_id
	if(json_resource.get("name")):
		collection.stf_name = json_resource["name"]
		collection.stf_name_source_of_truth = True
	bpy.context.scene.collection.children.link(collection)
	collection.stf_use_collection_as_prefab = True

	node_import_context = STF_ResourceImportContext(context, json_resource, collection)
	for node_id in json_resource.get("root_nodes", []):
		node_import_context.import_resource(node_id)

	# TODO animations

	return collection, node_import_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
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

	node_export_context = STF_ResourceExportContext(context, ret, collection)

	for blender_object in collection.all_objects[:]:
		if(type(blender_object) is bpy.types.Object and blender_object.parent == None):
			root_nodes.append(node_export_context.serialize_resource(blender_object))

	for action in bpy.data.actions:
		if(stf_animation_id := node_export_context.serialize_resource(action)):
			animations.append(stf_animation_id)

	return ret, collection.stf_id, node_export_context


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
	bpy.types.Collection.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Collection.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Collection.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Collection.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Collection.stf_active_component_index = bpy.props.IntProperty()

	bpy.types.Collection.stf_use_collection_as_prefab = bpy.props.BoolProperty(name="Use As STF Prefab", default=False)

def unregister():
	if hasattr(bpy.types.Collection, "stf_id"):
		del bpy.types.Collection.stf_id
	if hasattr(bpy.types.Collection, "stf_name"):
		del bpy.types.Collection.stf_name
	if hasattr(bpy.types.Collection, "stf_name_source_of_truth"):
		del bpy.types.Collection.stf_name_source_of_truth
	if hasattr(bpy.types.Collection, "stf_components"):
		del bpy.types.Collection.stf_components
	if hasattr(bpy.types.Collection, "stf_active_component_index"):
		del bpy.types.Collection.stf_active_component_index

	if hasattr(bpy.types.Collection, "stf_use_collection_as_prefab"):
		del bpy.types.Collection.stf_use_collection_as_prefab
