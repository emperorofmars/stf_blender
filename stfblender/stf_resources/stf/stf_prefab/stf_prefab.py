import bpy
from typing import Any

from .....stfblender_common import STF_ImportContext, STF_ExportContext, STF_Handler_ComponentHolder, STF_TaskSteps, STFReportSeverity, STF_Category, STFReport, STF_Handler_BlenderNative, STF_Data_Ref, boilerplate_register, boilerplate_unregister, get_components_from_object, ensure_stf_id


_stf_type = "stf.prefab"


class Handler_STF_Prefab(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["prefab"]
	understood_blender_types = [bpy.types.Collection]

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		collection = bpy.data.collections.new(json_resource.get("name", context.get_filename()))
		collection.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			collection.stf_info.stf_name = json_resource["name"]
			collection.stf_info.stf_name_source_of_truth = True
		bpy.context.scene.collection.children.link(collection)
		context.set_root_collection(collection)

		for node_id in json_resource.get("root_nodes", []):
			context.import_resource(json_resource, node_id, context_object=collection, stf_category=STF_Category.NODE)

		def _handle_animations():
			for animation_id in json_resource.get("animations", []):
				context.import_resource(json_resource, animation_id, context_object=collection, stf_category=STF_Category.DATA)
		context.add_task(STF_TaskSteps.ANIMATION, _handle_animations)

		return collection

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: Any, context_resource: Any | None) -> tuple[dict, str] | STFReport:
		collection: bpy.types.Collection = blender_resource
		ensure_stf_id(context, collection)

		root_nodes = []
		animations = []
		ret = {
			"type": _stf_type,
			"name": collection.stf_info.stf_name if collection.stf_info.stf_name_source_of_truth else collection.name,
			"root_nodes": root_nodes,
			"animations": animations,
		}

		for blender_resource in collection.all_objects[:]:
			if(type(blender_resource) is bpy.types.Object and blender_resource.parent is None):
				root_nodes.append(context.serialize_resource(ret, blender_resource, context_object=collection, stf_category="node", export_fail_severity=STFReportSeverity.FatalError))

		def _handle_animations():
			for action in bpy.data.actions:
				stf_animation_id = context.serialize_resource(ret, action, context_object=collection, stf_category="data", export_fail_severity=STFReportSeverity.Debug)
				if(stf_animation_id is not None):
					animations.append(stf_animation_id)
		context.add_task(STF_TaskSteps.ANIMATION, _handle_animations)

		return ret, collection.stf_info.stf_id

	get_components = get_components_from_object


def register():
	boilerplate_register(bpy.types.Collection)

	# STF-Data modules are stored on Collections
	bpy.types.Collection.stf_data_refs = bpy.props.CollectionProperty(type=STF_Data_Ref, name="STF Data Refs", options=set())
	bpy.types.Collection.stf_data_ref_selected = bpy.props.IntProperty(options=set())

def unregister():
	# STF-Data modules are stored on Collections
	if hasattr(bpy.types.Collection, "stf_data_ref_selected"):
		del bpy.types.Collection.stf_data_ref_selected
	if hasattr(bpy.types.Collection, "stf_data_refs"):
		del bpy.types.Collection.stf_data_refs

	boilerplate_unregister(bpy.types.Collection)

