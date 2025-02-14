import bpy
import mathutils

from ....libstf.stf_report import STFReport, STFReportSeverity
from ....libstf.stf_import_context import STF_ResourceImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext
from ...utils import trs_utils
from ...utils.id_utils import ensure_stf_id


def import_node_spatial_base(context: STF_ResourceImportContext, json_resource: dict, id: str, parent_application_object: any, blender_object: bpy.types.Object) -> tuple[any, any]:
	blender_object.stf_id = id
	if(json_resource.get("name")):
		blender_object.stf_name = json_resource["name"]
		blender_object.stf_name_source_of_truth = True
	blender_object.name = json_resource.get("name", "STF Node")
	for collection in blender_object.users_collection:
		collection.objects.unlink(blender_object)

	parent_application_object.objects.link(blender_object)

	for child_id in json_resource.get("children", []):
		child: bpy.types.Object = context.import_resource(child_id)
		if(child):
			child.parent_type = "OBJECT"
			child.parent = blender_object
			child.matrix_parent_inverse = mathutils.Matrix()
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, id, json_resource["type"], blender_object))

	if("parent_binding" in json_resource and json_resource["parent_binding"]):
		def _parent_binding_callback():
			parent_bindings = []
			for id_binding in json_resource["parent_binding"]:
				parent_bindings.append(context.get_imported_resource(id_binding))

			if(len(parent_bindings) == 2 and (hasattr(parent_bindings[0], "stf_id") and parent_bindings[0].stf_id == json_resource["parent_binding"][0])):
				# TODO deal with arbitrary depths of parent bindings and prefab instance bindings at that
				blender_object.parent = parent_bindings[0]
				blender_object.parent_type = "BONE"
				blender_object.parent_bone = parent_bindings[1].name
			else:
				context.report(STFReport("Invalid Parent Binding Target: " + str(json_resource["parent_binding"]), STFReportSeverity.Error, id, json_resource["type"], blender_object))
		context.add_task(_parent_binding_callback)

	def _trs_callback():
		trs_utils.trs_to_blender_object(json_resource["trs"], blender_object)
	context.add_task(_trs_callback)

	return blender_object, context


def export_node_spatial_base(context: STF_ResourceExportContext, blender_object: bpy.types.Object, parent_application_object: any, json_resource: dict) -> tuple[dict, str, any]:
	ensure_stf_id(context, blender_object)
	json_resource["name"] = blender_object.stf_name if blender_object.stf_name_source_of_truth else blender_object.name

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

	json_resource["children"] = children

	# TODO do this in a callback and check if the referenced resources are within the exported file
	if(blender_object.parent):
		match(blender_object.parent_type):
			case "OBJECT":
				# TODO check if object is a prefab instance and deal with that
				pass
			case "BONE":
				json_resource["parent_binding"] = [blender_object.parent.stf_id, blender_object.parent.data.bones[blender_object.parent_bone].stf_id]
			case _:
				context.report(STFReport("Unsupported object parent_type: " + str(blender_object.parent_type), STFReportSeverity.Error, blender_object.stf_id, json_resource.get("type"), blender_object))

	json_resource["trs"] = trs_utils.blender_object_to_trs(blender_object)

	if(blender_object.hide_render):
		json_resource["enabled"] = False

	return json_resource, blender_object.stf_id, context
