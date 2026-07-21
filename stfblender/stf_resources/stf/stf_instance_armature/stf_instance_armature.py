import bpy
import mathutils
import math
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STFReportSeverity, STFReport, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STF_Handler_BlenderNative, STF_Handler_Animation, STF_ComponentBoneInstanceRef, ensure_stf_id, STFSetIDOperatorBase
from .....stfblender_common.utils.animation_conversion_utils import *
from .....stfblender_common.utils.armature_bone import ArmatureBone
from .....stfblender_common.utils.trs_utils import close_enough
from .....stfblender_common.helpers import get_resource_id
from .stf_instance_armature_ui import STFSetArmatureInstanceIDOperator, draw_armature_instance_ui
from .stf_instance_armature_utils import parse_standin, process_components, serialize_standin, update_armature_instance_component_standins


_stf_type = "stf.instance.armature"


class STF_Instance_Armature(bpy.types.PropertyGroup):
	stf_components: bpy.props.CollectionProperty(type=STF_ComponentBoneInstanceRef, options=set()) # type: ignore
	stf_active_component_index: bpy.props.IntProperty(options=set()) # type: ignore


class Handler_STF_Instance_Armature(STF_Handler_BlenderNative, STF_Handler_Animation):
	stf_type = _stf_type
	stf_category = STF_Category.INSTANCE
	like_types = ["instance.armature", "instance"]
	understood_blender_types = [tuple]

	get_stf_prop_holder = lambda blender_resource: blender_resource[0].stf_instance
	operator_set_stf_id = STFSetArmatureInstanceIDOperator.bl_idname

	draw = draw_armature_instance_ui

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		blender_armature = context.import_resource(json_resource, json_resource["armature"], stf_category=STF_Category.DATA)
		if(not blender_armature or type(blender_armature) is not bpy.types.Armature):
			return STFReport("Failed to import armature: " + str(json_resource.get("instance", {}).get("armature")), STFReportSeverity.Error, stf_id, _stf_type, context_resource)

		blender_object = bpy.data.objects.new("STF Instance", blender_armature)
		blender_object.stf_instance.stf_id = stf_id
		if(json_resource.get("name")):
			blender_object.stf_instance.stf_name = json_resource["name"]

		bpy.context.scene.collection.objects.link(blender_object)
		context.register_imported_resource(stf_id, (blender_object, blender_armature))

		if("pose" in json_resource):
			if(bpy.context.mode != "OBJECT"): bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
			bpy.context.view_layer.objects.active = blender_object
			bpy.ops.object.mode_set(mode="POSE", toggle=False)
			bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

			if(blender_object.pose):
				root_poses = []
				next_poses = [bone for bone in blender_object.pose.bones if bone.parent == None]
				while(len(next_poses) > 0):
					root_poses = next_poses; next_poses = []
					for pose in root_poses:
						bone_id = blender_armature.bones[pose.name].stf_info.stf_id

						blender_matrix = mathutils.Matrix.LocRotScale(
							mathutils.Vector((json_resource["pose"][bone_id][0][0], json_resource["pose"][bone_id][0][1], json_resource["pose"][bone_id][0][2])), # pyright: ignore[reportArgumentType]
							mathutils.Quaternion((json_resource["pose"][bone_id][1][3], json_resource["pose"][bone_id][1][0], json_resource["pose"][bone_id][1][1], json_resource["pose"][bone_id][1][2])),
							mathutils.Vector((json_resource["pose"][bone_id][2][0], json_resource["pose"][bone_id][2][1], json_resource["pose"][bone_id][2][2])) # pyright: ignore[reportArgumentType]
						)
						if(pose.parent):
							pose.matrix = pose.parent.matrix @ blender_matrix
						else:
							pose.matrix = mathutils.Matrix.Rotation(math.radians(90), 4, "X") @ blender_matrix
						if(not blender_armature.bones[pose.name].use_deform):
							if(blender_armature.bones[pose.name].stf_bone.non_deform_use in ["ik_target", "ik_pole"]):
								pose.color.palette = "THEME03"
						next_poses += pose.children
			else:
				context.report(STFReport("Failed to import pose for armature: " + str(json_resource.get("armature")), STFReportSeverity.Error, stf_id, _stf_type, blender_armature))

		# components that exist on bones of this armature instance
		if("added_components" in json_resource):
			for bone_id, component_ids in json_resource["added_components"].items():
				for component_id_index in component_ids:
					if(component := context.import_resource(json_resource, component_id_index, blender_object, stf_category=STF_Category.COMPONENT)):
						component_id = get_resource_id(json_resource, component_id_index)
						for component_ref_index, component_ref in enumerate(blender_object.stf_info.stf_components):
							if(component_ref.stf_id == component_id):
								instance_component_ref = blender_object.stf_instance_armature.stf_components.add()
								instance_component_ref.stf_id = component_id
								instance_component_ref.stf_type = component_ref.stf_type
								instance_component_ref.blender_property_name = component_ref.blender_property_name
								instance_component_ref.bone = context.get_imported_resource(get_resource_id(json_resource, bone_id)).name  # pyright: ignore[reportArgumentType]
								blender_object.stf_info.stf_components.remove(component_ref_index)
								break

		# changes to bone component values for this armature instance only
		update_armature_instance_component_standins(bpy.context, blender_object)
		if("modified_components" in json_resource):
			for bone_id, component_ids in json_resource["modified_components"].items():
				for component_id, standin_component_json in component_ids.items():
					parse_standin(context, blender_object, component_id, standin_component_json)

		def _run_component_process():
			process_components(blender_object, [stf_resource for _, stf_resource in context._state._resources.items()])
		context.add_task(STF_TaskSteps.BEFORE_ANIMATION, _run_component_process)

		return blender_object

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str] | STFReport:
		blender_object: bpy.types.Object = blender_resource[0]
		blender_armature: bpy.types.Armature = blender_resource[1]

		ensure_stf_id(context, blender_object.stf_instance)
		ret = {"type": _stf_type, "name": blender_object.stf_instance.stf_name}

		ret["armature"] = context.serialize_resource(ret, blender_armature, stf_category="data")

		if(blender_object.pose):
			stf_pose: dict[str, list[list[float]]] = {}
			for blender_pose in blender_object.pose.bones:
				# let t, r, s
				if blender_pose.parent:
					t, r, s = (blender_pose.parent.matrix.inverted_safe() @ blender_pose.matrix).decompose()
				else:
					t, r, s = (mathutils.Matrix.Rotation(math.radians(-90), 4, "X") @ blender_pose.matrix).decompose()

				# already in armature space, so no trs_utils conversion
				stf_pose[blender_armature.bones[blender_pose.name].stf_info.stf_id] = [
					[close_enough(t[0]), close_enough(t[1]), close_enough(t[2])],
					[close_enough(r[1]), close_enough(r[2]), close_enough(r[3]), close_enough(r[0], 1)],
					[close_enough(s[0], 1), close_enough(s[1], 1), close_enough(s[2], 1)]
				]
			ret["pose"] = stf_pose

		# components that exist on bones of this armature instance
		if(len(blender_object.stf_instance_armature.stf_components) > 0):
			added_components = {}
			for component_ref in blender_object.stf_instance_armature.stf_components:
				components = getattr(blender_object, component_ref.blender_property_name)
				for component in components:
					if(component.stf_id == component_ref.stf_id and component_ref.bone):
						bone = blender_armature.bones[component_ref.bone]
						component_id = context.serialize_resource(ret, component, blender_object, "component")
						if(component_id):
							if(bone.stf_info.stf_id not in added_components):
								added_components[bone.stf_info.stf_id] = []
							added_components[bone.stf_info.stf_id].append(component_id)
			ret["added_components"] = added_components

		# changes to bone component values for this armature instance only
		if(len(blender_object.stf_instance_armature_component_standins.stf_components) > 0):
			modified_components = {}
			for component_ref in blender_object.stf_instance_armature_component_standins.stf_components:
				if(component_ref.override):
					bone = blender_armature.bones[component_ref.bone]
					if(hasattr(bone, component_ref.blender_property_name)):
						for bone_component_ref in getattr(bone, component_ref.blender_property_name):
							if(bone_component_ref.stf_id == component_ref.stf_id):
								break
						else:
							continue # skip, doesn't exist anymore
					standin_override = serialize_standin(context, blender_object, component_ref)
					if(standin_override):
						if(bone.stf_info.stf_id not in modified_components):
							modified_components[bone.stf_info.stf_id] = {}
						modified_components[bone.stf_info.stf_id][component_ref.stf_id] = standin_override
			ret["modified_components"] = modified_components

		return ret, blender_object.stf_instance.stf_id

	@staticmethod
	def can_handle_blender_resource(blender_resource: Any) -> int:
		if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and type(blender_resource[1]) is bpy.types.Armature):
			return 1000
		else:
			return -1

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = ["pose.bones"]

	@staticmethod
	def export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
		import re
		if(match := re.search(r"^pose.bones\[\"(?P<bone_name>[\w. -:,]+)\"\]", blender_property_path)):
			if(type(blender_resource.data) is not bpy.types.Armature or match.groupdict()["bone_name"] not in blender_resource.data.bones):
				return None
			return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance"]) + context.resolve_application_property_path(ArmatureBone(blender_resource.data, match.groupdict()["bone_name"]), property_index, blender_property_path[match.span()[1] :])
		return None

	@staticmethod
	def import_stf_animation_property_path_func(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
		return context.resolve_stf_property_path(stf_property_path[1:], blender_resource)


def register():
	bpy.types.Object.stf_instance_armature = bpy.props.PointerProperty(type=STF_Instance_Armature)
	bpy.types.Object.stf_instance_armature_component_standins = bpy.props.PointerProperty(type=STF_Instance_Armature)

def unregister():
	if hasattr(bpy.types.Object, "stf_instance_armature"):
		del bpy.types.Object.stf_instance_armature
	if hasattr(bpy.types.Object, "stf_instance_armature_component_standins"):
		del bpy.types.Object.stf_instance_armature_component_standins
