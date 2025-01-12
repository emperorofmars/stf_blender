import bpy
import mathutils

from ....libstf.stf_report import STFReportSeverity, STFReport
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils import trs_utils
from ...utils.id_binding_resolver import resolve_id_binding
from ..stf_prefab.stf_prefab import STF_BlenderNodeExportContext, STF_BlenderNodeImportContext


_stf_type = "stf.node.spatial"


def _stf_import(context: STF_BlenderNodeImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> tuple[any, any]:
	blender_object: bpy.types.Object = None
	if(import_hook_results and len(import_hook_results) == 1):
		blender_object: bpy.types.Object = import_hook_results[0]
		#blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), import_hook_results[0])
		blender_object.name = json_resource.get("name", "STF Node")
	else:
		blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)
		if(import_hook_results and len(import_hook_results) > 1):
			pass # TODO create child objects per hook object
	blender_object.stf_id = id
	blender_object.stf_name = json_resource.get("name", "")
	for collection in blender_object.users_collection:
		collection.objects.unlink(blender_object)

	parent_application_object.objects.link(blender_object)

	if(import_hook_results and len(import_hook_results) > 1):
		for hook_result in import_hook_results:
			hook_result.stf_is_component_stand_in = True
			hook_result.parent = blender_object
			parent_application_object.objects.link(hook_result)

	for child_id in json_resource.get("children", []):
		child: bpy.types.Object = context.import_resource(child_id)
		if(child):
			child.parent_type = "OBJECT"
			child.parent = blender_object
			child.matrix_parent_inverse = mathutils.Matrix()
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, id, _stf_type, blender_object))

	if("parent_binding" in json_resource and json_resource["parent_binding"]):
		def _parent_binding_callback():
			parent_bindings = []
			for id_binding in json_resource["parent_binding"]:
				parent_bindings.append(context.get_imported_resource(id_binding))

			if(len(parent_bindings) == 2 and (hasattr(parent_bindings[0], "stf_data_id") and parent_bindings[0].stf_data_id == json_resource["parent_binding"][0])):
				# TODO deal with arbitrary depths of parent bindings and prefab instance bindings at that
				blender_object.parent = parent_bindings[0]
				blender_object.parent_type = "BONE"
				blender_object.parent_bone = parent_bindings[1].name
			else:
				context.report(STFReport("Invalid Parent Binding Target: " + str(json_resource["parent_binding"]), STFReportSeverity.Error, id, _stf_type, blender_object))
		context.add_task(_parent_binding_callback)

	def _trs_callback():
		trs_utils.trs_to_blender_object(json_resource["trs"], blender_object)
	context.add_task(_trs_callback)

	return blender_object, context


def _stf_export(context: STF_BlenderNodeExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ensure_stf_id(context, blender_object)

	children = []
	for child in blender_object.children:
		# Child objects can be part of different collections. However, if none of its collections are enabled, do not export it.
		object_exists = False
		for collection in child.users_collection:
			for layer_collection in bpy.context.view_layer.layer_collection.children:
				if(collection.name == layer_collection.name):
					if(not layer_collection.exclude):
						object_exists = True
						break
			if(object_exists): break

		if(object_exists):
			children.append(context.serialize_resource(child))

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_name if blender_object.stf_name else blender_object.name,
		"children": children
	}

	# TODO do this in a callback and check if the referenced resources are within the exported file
	if(blender_object.parent):
		match(blender_object.parent_type):
			case "OBJECT":
				# TODO check if object is a prefab instance and deal with that
				pass
			case "BONE":
				ret["parent_binding"] = [blender_object.parent.stf_data_id, blender_object.parent.data.bones[blender_object.parent_bone].stf_id]
			case _:
				context.report(STFReport("Unsupported object parent_type: " + str(blender_object.parent_type), STFReportSeverity.Error, blender_object.stf_id, _stf_type, blender_object))

	ret["trs"] = trs_utils.blender_object_to_trs(blender_object)

	if(blender_object.hide_render):
		ret["enabled"] = False

	return ret, blender_object.stf_id, context


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
	bpy.types.Object.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Object.stf_is_component_stand_in = bpy.props.BoolProperty(name="Object Represents Component", default=False) # type: ignore
	bpy.types.Object.stf_data_id = bpy.props.StringProperty(name="Data Component ID") # type: ignore
	bpy.types.Object.stf_data_name = bpy.props.StringProperty(name="Data Component Name") # type: ignore
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_name"):
		del bpy.types.Object.stf_name
	if hasattr(bpy.types.Object, "stf_is_component_stand_in"):
		del bpy.types.Object.stf_is_component_stand_in
	if hasattr(bpy.types.Object, "stf_data_id"):
		del bpy.types.Object.stf_data_id
	if hasattr(bpy.types.Object, "stf_data_name"):
		del bpy.types.Object.stf_data_name
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index
