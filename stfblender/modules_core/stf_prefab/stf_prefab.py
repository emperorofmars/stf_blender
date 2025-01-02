import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_processor import STF_Processor
from ...utils.component_utils import STF_Component
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


def _stf_import(context: STF_ImportContext, json: dict, id: str) -> any:
	pass

def _stf_export(context: STF_RootExportContext, application_object: any) -> tuple[dict, str, any]:
	collection: bpy.types.Collection = application_object
	ensure_stf_id(collection)

	root_nodes = []
	ret = {
		"type": _stf_type,
		"name": collection.name,
		"root_nodes": root_nodes,
	}

	node_export_context = STF_BlenderNodeExportContext(context, ret)
	for blender_object in collection.all_objects:
		if(blender_object.parent == None):
			root_nodes.append(node_export_context.serialize_resource(blender_object))

	"""if(len(collection.stf_components) > 0):
		components = ret["components"] = {}
		for component in collection.stf_components:
			print(str(component))
			print(str(component.stf_id))
			print(str(component.stf_type))
			# TODO export components

			#context.serialize_resource()"""

	return ret, collection.stf_id, node_export_context


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
	bpy.types.Collection.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Collection.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Collection.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Collection, "stf_id"):
		del bpy.types.Collection.stf_id
	if hasattr(bpy.types.Collection, "stf_components"):
		del bpy.types.Collection.stf_components
	if hasattr(bpy.types.Collection, "stf_active_component_index"):
		del bpy.types.Collection.stf_active_component_index
