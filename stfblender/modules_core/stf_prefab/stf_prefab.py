import bpy


from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReport
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.prefab"


class STF_BlenderNodeExportContext(STF_ResourceExportContext):
	def ensure_resource_properties(self):
		super().ensure_resource_properties()
		if(not hasattr(self._json_resource, "nodes")):
			self._json_resource["nodes"] = {}

	def get_resource_id(self, application_object: any) -> str | None:
		if(type(application_object) is bpy.types.Object):
			if(application_object.stf_id and application_object.stf_id in self._json_resource["nodes"].keys()):
				return application_object.stf_id
			else:
				return None
		else:
			return super().get_resource_id(application_object)

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		if(type(application_object) is bpy.types.Object):
			self._json_resource["nodes"][id] = json_resource
		else:
			super().register_serialized_resource(application_object, json_resource, id)


class STF_BlenderNodeImportContext(STF_ResourceImportContext):
	def get_json_resource(self, id: str) -> dict:
		if(id in self._json_resource["nodes"]):
			return self._json_resource["nodes"][id]
		else:
			return super().get_json_resource(id)

	def register_imported_resource(self, id: str, application_object: any):
		if(type(application_object) is bpy.types.Object):
			pass
		else:
			super().register_imported_resource(application_object, id)


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> tuple[any, any]:
	collection = bpy.data.collections.new(json_resource.get("name", context.get_filename()))
	collection.stf_id = id
	collection.stf_name = json_resource.get("name", "")
	bpy.context.scene.collection.children.link(collection)
	collection.metric_multiplier = json_resource.get("metric_multiplier", 1)

	node_import_context = STF_BlenderNodeImportContext(context, json_resource, collection)
	for node_id in json_resource.get("root_nodes", []):
		node_import_context.import_resource(node_id)
	return collection, node_import_context

def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	collection: bpy.types.Collection = application_object
	ensure_stf_id(collection)

	root_nodes = []
	ret = {
		"type": _stf_type,
		"name": collection.stf_name if collection.stf_name else collection.name,
		"root_nodes": root_nodes,
		"metric_multiplier": collection.metric_multiplier,
	}

	node_export_context = STF_BlenderNodeExportContext(context, ret, collection)
	for blender_object in collection.all_objects:
		if(blender_object.parent == None):
			root_nodes.append(node_export_context.serialize_resource(blender_object))

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
	bpy.types.Collection.metric_multiplier = bpy.props.FloatProperty(name="Metric Multiplier", default=1, min=0.00000001) # type: ignore
	bpy.types.Collection.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Collection.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Collection, "stf_id"):
		del bpy.types.Collection.stf_id
	if hasattr(bpy.types.Collection, "stf_name"):
		del bpy.types.Collection.stf_name
	if hasattr(bpy.types.Collection, "metric_multiplier"):
		del bpy.types.Collection.metric_multiplier
	if hasattr(bpy.types.Collection, "stf_components"):
		del bpy.types.Collection.stf_components
	if hasattr(bpy.types.Collection, "stf_active_component_index"):
		del bpy.types.Collection.stf_active_component_index
