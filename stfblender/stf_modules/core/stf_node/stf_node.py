import math
import bpy
import mathutils

from ....base.stf_module import STF_Module
from ....importer.stf_import_context import STF_ImportContext
from ....exporter.stf_export_context import STF_ExportContext
from ....base.stf_report import STFReport, STFReportSeverity
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister
from ....utils.component_utils import get_components_from_object
from ....utils import trs_utils
from ....utils.id_utils import ensure_stf_id
from .node_property_conversion import stf_node_resolve_property_path_to_stf_func, stf_node_resolve_stf_property_to_blender_func


_stf_type = "stf.node"


class STF_Instance(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="Name", options=set()) # type: ignore
	enabled: bpy.props.BoolProperty(name="Enabled", default=True, options=set()) # type: ignore


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	if("instance" in json_resource):
		blender_object: bpy.types.Object = context.import_resource(json_resource["instance"], stf_kind="instance")
	else:
		blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), None)
	context.register_imported_resource(stf_id, blender_object)

	blender_object.stf_info.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_info.stf_name = json_resource["name"]
		blender_object.stf_info.stf_name_source_of_truth = True
	blender_object.name = json_resource.get("name", "STF Node")
	for collection in blender_object.users_collection:
		collection.objects.unlink(blender_object)
	context_object.objects.link(blender_object)

	blender_object.rotation_mode = "QUATERNION"

	def _handle_parenting():
		matrix_local = trs_utils.stf_to_blender_matrix(json_resource["trs"])
		if(blender_object.parent):
			if("parent_binding" in json_resource and json_resource["parent_binding"] and len(json_resource["parent_binding"]) == 3):
				bone: bpy.types.Bone = context.get_imported_resource(json_resource["parent_binding"][2]).get_bone()
				pose_bone = blender_object.parent.pose.bones[bone.name]
				blender_object.parent_type = "BONE"
				blender_object.parent_bone = bone.name
				blender_object.matrix_parent_inverse = (blender_object.parent.matrix_world @ mathutils.Matrix.Translation(pose_bone.tail - pose_bone.head) @ pose_bone.matrix).inverted_safe() # Blender why
				blender_object.matrix_world = blender_object.parent.matrix_world @ pose_bone.matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X") @ matrix_local # Blender why
			else:
				blender_object.parent_type = "OBJECT"
				blender_object.matrix_parent_inverse = blender_object.parent.matrix_world.inverted_safe()
				blender_object.matrix_world = blender_object.parent.matrix_world @ matrix_local
		else:
			blender_object.matrix_world = matrix_local
	context.add_task(_handle_parenting)

	for child_id in json_resource.get("children", []):
		child: bpy.types.Object = context.import_resource(child_id, context_object, stf_kind="node")
		if(child):
			child.parent = blender_object
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, stf_id, json_resource["type"], blender_object))

	if("enabled" in json_resource and json_resource["enabled"] == False):
		blender_object.hide_render = True

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object):
		if(not application_object.instance_collection and not application_object.data):
			return 1000
		else:
			return 0
	else:
		return -1


def _stf_export(context: STF_ExportContext, blender_object: bpy.types.Object, context_object: bpy.types.Collection) -> tuple[dict, str]:
	ensure_stf_id(context, blender_object)

	json_resource = {
		"type": _stf_type,
		"name": blender_object.stf_info.stf_name if blender_object.stf_info.stf_name_source_of_truth else blender_object.name
	}

	children = []
	for child in blender_object.children:
		for collection in child.users_collection:
			if(collection == context_object):
				children.append(context.serialize_resource(child, context_object, module_kind="node"))
				break # break inner loop

	json_resource["children"] = children

	# TODO Check if the referenced resources are within the exported file
	def _handle_parent_binding():
		if(blender_object.parent):
			match(blender_object.parent_type):
				case "OBJECT":
					pass
				case "BONE":
					# TODO make this more generic
					json_resource["parent_binding"] = [blender_object.parent.stf_info.stf_id, "instance", blender_object.parent.data.bones[blender_object.parent_bone].stf_info.stf_id]
				case _:
					context.report(STFReport("Unsupported object parent_type: " + str(blender_object.parent_type), STFReportSeverity.FatalError, blender_object.stf_info.stf_id, json_resource.get("type"), blender_object))
	context.add_task(_handle_parent_binding)

	# let t, r, s
	if(blender_object.parent):
		if(blender_object.parent_type == "OBJECT"):
			t, r, s = (blender_object.parent.matrix_world.inverted_safe() @ blender_object.matrix_world).decompose()
		elif(blender_object.parent_type == "BONE" and blender_object.parent_bone):
			t, r, s = ((blender_object.parent.matrix_world @ (blender_object.parent.pose.bones[blender_object.parent_bone].matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X"))).inverted_safe() @ blender_object.matrix_world).decompose() # Blender why
	else:
		t, r, s = blender_object.matrix_world.decompose()
	json_resource["trs"] = trs_utils.blender_to_trs(t, r, s)

	if(blender_object.hide_render):
		json_resource["enabled"] = False

	if(blender_object.data):
		instance_id = context.serialize_resource((blender_object, blender_object.data), module_kind="instance")
		if(instance_id):
			json_resource["instance"] = instance_id

	return json_resource, blender_object.stf_info.stf_id


class STF_Module_STF_Node(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["node", "node.spatial"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["location", "rotation_quaternion", "rotation_euler", "scale", "hide_render"]
	resolve_property_path_to_stf_func = stf_node_resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = stf_node_resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Node
]


def register():
	boilerplate_register(bpy.types.Object, "node")
	bpy.types.Object.stf_instance = bpy.props.PointerProperty(type=STF_Instance, options=set()) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stf_instance"):
		del bpy.types.Object.stf_instance
	boilerplate_unregister(bpy.types.Object, "node")
