import bpy
from typing import Any

from .....stf_blender_common.protocols import PSTF_ExportContext, PSTF_ImportContext, STF_Handler_BlenderNative
from .....stf_blender_common.protocols.stf_info import boilerplate_register, boilerplate_unregister
from .....stf_blender_common.base import STF_TaskSteps, STF_Category, STFReport, STFReportSeverity
from .....stf_blender_common.utils.id_utils import ensure_stf_id
from .....stf_blender_common.utils.component_resource_utils import get_components_from_object


_stf_type = "stf.prefab"


def _stf_import(context: PSTF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any | STFReport:
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

def _stf_export(context: PSTF_ExportContext, blender_object: Any, context_object: Any | None) -> tuple[dict, str] | STFReport:
	collection: bpy.types.Collection = blender_object
	ensure_stf_id(context, collection)

	root_nodes = []
	animations = []
	ret = {
		"type": _stf_type,
		"name": collection.stf_info.stf_name if collection.stf_info.stf_name_source_of_truth else collection.name,
		"root_nodes": root_nodes,
		"animations": animations,
	}

	for blender_object in collection.all_objects[:]:
		if(type(blender_object) is bpy.types.Object and blender_object.parent is None):
			root_nodes.append(context.serialize_resource(ret, blender_object, context_object=collection, stf_category="node", export_fail_severity=STFReportSeverity.FatalError))

	def _handle_animations():
		for action in bpy.data.actions:
			stf_animation_id = context.serialize_resource(ret, action, context_object=collection, stf_category="data", export_fail_severity=STFReportSeverity.Debug)
			if(stf_animation_id is not None):
				animations.append(stf_animation_id)
	context.add_task(STF_TaskSteps.ANIMATION, _handle_animations)

	return ret, collection.stf_info.stf_id


class Handler_STF_Prefab(STF_Handler_BlenderNative):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["prefab"]
	understood_application_types = [bpy.types.Collection]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_handlers = [
	Handler_STF_Prefab
]

def register():
	boilerplate_register(bpy.types.Collection)

def unregister():
	boilerplate_unregister(bpy.types.Collection)
