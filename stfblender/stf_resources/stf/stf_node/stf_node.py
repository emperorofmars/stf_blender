import bpy
import math
import mathutils
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STFReportSeverity, STFReport, STF_Category, STF_Handler_BlenderNative, STF_Handler_Animation, STF_Handler_ComponentHolder, boilerplate_register, boilerplate_unregister, get_components_from_object, ensure_stf_id
from .....stfblender_common.utils import trs_utils
from .....stfblender_common.helpers import get_resource_id, register_exported_resource, draw_multiline_text
from .node_property_conversion import stf_node_export_blender_animation, stf_node_import_stf_animation_property_path_func
from .stf_node_ops import STFAddObjectComponentOperator, STFEditObjectComponentIdOperator, STFNodeFixRotationMode, STFRemoveObjectComponentOperator, STFSetObjectIDOperator


_stf_type = "stf.node"


class STF_Instance(bpy.types.PropertyGroup):
	stf_id: bpy.props.StringProperty(name="ID", options=set())
	stf_name: bpy.props.StringProperty(name="Name", options=set())
	enabled: bpy.props.BoolProperty(name="Enabled", default=True, options=set())


class Handler_STF_Node(STF_Handler_BlenderNative, STF_Handler_ComponentHolder, STF_Handler_Animation):
	stf_type = _stf_type
	stf_category = STF_Category.NODE
	like_types = ["node", "node.spatial"]
	understood_blender_types = [bpy.types.Object]

	operator_set_stf_id = STFSetObjectIDOperator.bl_idname

	@staticmethod
	def draw(layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: bpy.types.Object) -> None | bool:
		if(context.object.rotation_mode != "QUATERNION"):
			text_row = draw_multiline_text(layout, "Please set the Rotation-Mode to 'Quaternion (WXYZ)'\nDoing so ensures consistency with game-engines.\nBe aware that existing rotation animations will break!", width=80, icon="ERROR", alert=True)
			row_fix = text_row.row()
			row_fix.alignment = "LEFT"
			text_row.operator(STFNodeFixRotationMode.bl_idname)
		else:
			return False # No UI has been drawn

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any | STFReport:
		if("instance" in json_resource):
			blender_object: bpy.types.Object = context.import_resource(json_resource, json_resource["instance"], stf_category=STF_Category.INSTANCE) # pyright: ignore[reportAssignmentType]
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
					bone: bpy.types.Bone = context.get_imported_resource(get_resource_id(json_resource, json_resource["parent_binding"][2])).get_bone() # pyright: ignore[reportArgumentType]
					pose_bone = blender_object.parent.pose.bones[bone.name]
					blender_object.parent_type = "BONE"
					blender_object.parent_bone = bone.name
					blender_object.matrix_parent_inverse = (blender_object.parent.matrix_world @ mathutils.Matrix.Translation(pose_bone.tail - pose_bone.head) @ pose_bone.matrix).inverted_safe() # pyright: ignore[reportArgumentType] # Blender why
					blender_object.matrix_world = blender_object.parent.matrix_world @ pose_bone.matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X") @ matrix_local # Blender why
				else:
					blender_object.parent_type = "OBJECT"
					blender_object.matrix_parent_inverse = blender_object.parent.matrix_world.inverted_safe()
					blender_object.matrix_world = blender_object.parent.matrix_world @ matrix_local
			else:
				blender_object.matrix_world = matrix_local
		context.add_task(STF_TaskSteps.DEFAULT, _handle_parenting)

		for child_id in json_resource.get("children", []):
			child: bpy.types.Object | None = context.import_resource(json_resource, child_id, context_object, stf_category=STF_Category.NODE)
			if(child):
				child.parent = blender_object
			else:
				context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, stf_id, json_resource["type"], blender_object))

		if("enabled" in json_resource and not json_resource["enabled"]):
			blender_object.hide_render = True

		return blender_object

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_object: bpy.types.Object, context_object: bpy.types.Collection) -> tuple[dict, str] | STFReport:
		ensure_stf_id(context, blender_object)

		json_resource = {
			"type": _stf_type,
			"name": blender_object.stf_info.stf_name if blender_object.stf_info.stf_name_source_of_truth else blender_object.name
		}

		children = []
		for child in blender_object.children:
			for collection in child.users_collection:
				if(context_object.is_embedded_data or collection == context_object):
					children.append(context.serialize_resource(json_resource, child, context_object, stf_category="node"))
					break # break inner loop

		json_resource["children"] = children

		def _handle_parent_binding():
			if(blender_object.parent):
				match(blender_object.parent_type):
					case "OBJECT":
						pass
					case "BONE":
						# This path works like animation paths
						json_resource["parent_binding"] = [register_exported_resource(json_resource, blender_object.parent.stf_info.stf_id), "instance", register_exported_resource(json_resource, blender_object.parent.data.bones[blender_object.parent_bone].stf_info.stf_id)]
					case _:
						context.report(STFReport("Unsupported object parent_type: " + str(blender_object.parent_type), STFReportSeverity.FatalError, blender_object.stf_info.stf_id, json_resource.get("type"), blender_object))
		context.add_task(STF_TaskSteps.DEFAULT, _handle_parent_binding)

		# let t, r, s
		if(blender_object.parent):
			if(blender_object.parent_type == "OBJECT"):
				t, r, s = (blender_object.parent.matrix_world.inverted_safe() @ blender_object.matrix_world).decompose()
			elif(blender_object.parent_type == "BONE" and blender_object.parent_bone):
				t, r, s = ((blender_object.parent.matrix_world @ (blender_object.parent.pose.bones[blender_object.parent_bone].matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X"))).inverted_safe() @ blender_object.matrix_world).decompose() # Blender why
		else:
			t, r, s = blender_object.matrix_world.decompose()
		json_resource["trs"] = trs_utils.blender_to_trs(t, r, s) # pyright: ignore[reportPossiblyUnboundVariable]

		if(blender_object.hide_render):
			json_resource["enabled"] = False

		if(blender_object.data):
			instance_id = context.serialize_resource(json_resource, (blender_object, blender_object.data), context_object, stf_category="instance")
			if(instance_id is not None):
				json_resource["instance"] = instance_id

		return json_resource, blender_object.stf_info.stf_id

	@classmethod
	def can_handle_blender_resource(cls, blender_resource: Any) -> int:
		if(type(blender_resource) is bpy.types.Object):
			if(not blender_resource.instance_collection and not blender_resource.data):
				return 1000
			else:
				return 0
		else:
			return -1

	get_components = get_components_from_object
	operator_component_add = STFAddObjectComponentOperator.bl_idname
	operator_component_remove = STFRemoveObjectComponentOperator.bl_idname
	operator_component_edit = STFEditObjectComponentIdOperator.bl_idname

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = ["location", "rotation_quaternion", "rotation_euler", "scale", "hide_render"]
	export_blender_animation = stf_node_export_blender_animation
	import_stf_animation_property_path_func = stf_node_import_stf_animation_property_path_func


def register():
	boilerplate_register(bpy.types.Object)
	bpy.types.Object.stf_instance = bpy.props.PointerProperty(type=STF_Instance, options=set()) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stf_instance"):
		del bpy.types.Object.stf_instance
	boilerplate_unregister(bpy.types.Object)
