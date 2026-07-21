import bpy
from typing import Any

from .....stfblender_common import STF_ImportContext, STF_ExportContext, STF_Category, STFReport
from .....stfblender_common.resource import STF_Handler_BlenderNative, STF_Handler_ComponentHolder, boilerplate_register, boilerplate_unregister, get_components_from_object, ensure_stf_id
from .....stfblender_common.utils.armature_bone import ArmatureBone
from .stf_armature_ops import STFAddArmatureComponentOperator, STFEditArmatureComponentIdOperator, STFRemoveArmatureComponentOperator, STFSetArmatureIDOperator


_stf_type = "stf.armature"


class Handler_STF_Armature(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["armature", "prefab"]
	understood_blender_types = [bpy.types.Armature]

	operator_set_stf_id = STFSetArmatureIDOperator.bl_idname

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		blender_armature = bpy.data.armatures.new(json_resource.get("name", "STF Armature"))
		blender_armature.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			blender_armature.stf_info.stf_name = json_resource["name"]
			blender_armature.stf_info.stf_name_source_of_truth = True
		tmp_hook_object: bpy.types.Object = bpy.data.objects.new("TRASH", blender_armature)
		context.register_trash_object(tmp_hook_object)
		bpy.context.scene.collection.objects.link(tmp_hook_object)

		for bone_id in json_resource.get("root_bones", []):
			context.import_resource(json_resource, bone_id, tmp_hook_object, STF_Category.NODE)

		return blender_armature

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str] | STFReport:
		blender_armature: bpy.types.Armature = blender_resource
		ensure_stf_id(context, blender_armature)

		tmp_hook_object: bpy.types.Object = bpy.data.objects.new("TRASH", blender_armature)
		context.register_trash_object(tmp_hook_object)
		bpy.context.scene.collection.objects.link(tmp_hook_object)

		root_bones = []
		ret = {
			"type": _stf_type,
			"name": blender_armature.stf_info.stf_name if blender_armature.stf_info.stf_name_source_of_truth else blender_armature.name,
			"root_bones": root_bones,
		}

		root_bone_definitions = []
		for blender_bone in blender_armature.bones:
			if(blender_bone.parent is None):
				root_bone_definitions.append(ArmatureBone(blender_armature, blender_bone.name))

		for root_bone_definition in root_bone_definitions:
			root_bones.append(context.serialize_resource(ret, root_bone_definition, blender_armature, "node"))

		return ret, blender_armature.stf_info.stf_id

	get_components = get_components_from_object
	operator_component_add = STFAddArmatureComponentOperator.bl_idname
	operator_component_remove = STFRemoveArmatureComponentOperator.bl_idname
	operator_component_edit = STFEditArmatureComponentIdOperator.bl_idname


def register():
	boilerplate_register(bpy.types.Armature)

def unregister():
	boilerplate_unregister(bpy.types.Armature)
