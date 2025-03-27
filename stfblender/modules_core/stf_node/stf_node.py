import bpy
import mathutils

from ....libstf.stf_module import STF_Module
from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_report import STFReport, STFReportSeverity
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils import trs_utils
from ...utils.id_utils import ensure_stf_id
from .node_property_conversion import stf_node_translate_property_to_stf_func, stf_node_translate_property_to_blender_func


_stf_type = "stf.node"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	if("instance" in json_resource):
		blender_object: bpy.types.Object = context.import_resource(json_resource["instance"])
	else:
		blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)
	context.register_imported_resource(stf_id, blender_object)

	blender_object.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_name = json_resource["name"]
		blender_object.stf_name_source_of_truth = True
	blender_object.name = json_resource.get("name", "STF Node")
	for collection in blender_object.users_collection:
		collection.objects.unlink(blender_object)

	context_object.objects.link(blender_object)

	for child_id in json_resource.get("children", []):
		child: bpy.types.Object = context.import_resource(child_id, context_object)
		if(child):
			child.parent_type = "OBJECT"
			child.parent = blender_object
			child.matrix_parent_inverse = mathutils.Matrix()
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, stf_id, json_resource["type"], blender_object))

	if("parent_binding" in json_resource and json_resource["parent_binding"]):
		def _parent_binding_callback():
			parent_bindings = []
			for id_binding in json_resource["parent_binding"]:
				parent_bindings.append(context.get_imported_resource(id_binding))

			if(len(parent_bindings) == 2 and (hasattr(parent_bindings[0], "stf_id") and parent_bindings[0].stf_id == json_resource["parent_binding"][0])):
				# TODO deal with arbitrary depths of parent bindings and prefab instance bindings eventually
				blender_object.parent = parent_bindings[0]
				blender_object.parent_type = "BONE"
				blender_object.parent_bone = parent_bindings[1].name
			else:
				context.report(STFReport("Invalid Parent Binding Target: " + str(json_resource["parent_binding"]), STFReportSeverity.Error, stf_id, json_resource["type"], blender_object))
		context.add_task(_parent_binding_callback)

	def _trs_callback():
		trs_utils.trs_to_blender_object(json_resource["trs"], blender_object)
	context.add_task(_trs_callback)

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object):
		if(not application_object.instance_collection and not application_object.data):
			return 1000
		else:
			return 0
	else:
		return -1


def _stf_export(context: STF_ExportContext, blender_object: any, context_object: any) -> tuple[dict, str]:
	ensure_stf_id(context, blender_object)

	json_resource = {
		"type": _stf_type,
		"name": blender_object.stf_name if blender_object.stf_name_source_of_truth else blender_object.name
	}

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

		if(object_exists and type(child) is bpy.types.Object):
			children.append(context.serialize_resource(child, module_kind="node"))

	json_resource["children"] = children

	# TODO do this in a callback and check if the referenced resources are within the exported file
	if(blender_object.parent):
		match(blender_object.parent_type):
			case "OBJECT":
				# TODO check if object is a prefab instance and deal with that
				pass
			case "BONE":
				# TODO make this the same as animation property targets
				json_resource["parent_binding"] = [blender_object.parent.stf_id, blender_object.parent.data.bones[blender_object.parent_bone].stf_id]
			case _:
				context.report(STFReport("Unsupported object parent_type: " + str(blender_object.parent_type), STFReportSeverity.Error, blender_object.stf_id, json_resource.get("type"), blender_object))

	json_resource["trs"] = trs_utils.blender_object_to_trs(blender_object)

	if(blender_object.hide_render):
		json_resource["enabled"] = False

	if(blender_object.data):
		instance_id = context.serialize_resource((blender_object, blender_object.data), module_kind="instance")
		if(instance_id):
			json_resource["instance"] = instance_id

	return json_resource, blender_object.stf_id



class STF_Module_STF_Node(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["node", "node.spatial"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	translate_property_to_stf_func = stf_node_translate_property_to_stf_func
	translate_property_to_blender_func: stf_node_translate_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Node
]


def register():
	bpy.types.Object.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Object.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Object.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Object.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Object.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Object, "stf_id"):
		del bpy.types.Object.stf_id
	if hasattr(bpy.types.Object, "stf_name"):
		del bpy.types.Object.stf_name
	if hasattr(bpy.types.Object, "stf_name_source_of_truth"):
		del bpy.types.Object.stf_name_source_of_truth
	if hasattr(bpy.types.Object, "stf_components"):
		del bpy.types.Object.stf_components
	if hasattr(bpy.types.Object, "stf_active_component_index"):
		del bpy.types.Object.stf_active_component_index
