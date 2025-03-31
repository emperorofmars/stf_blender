import bpy

from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import get_components_from_object
from ...utils.boilerplate import boilerplate_register, boilerplate_unregister
from ...utils.id_utils import ensure_stf_id
from ...utils.armature_bone import ArmatureBone


_stf_type = "stf.armature"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_armature = bpy.data.armatures.new(json_resource.get("name", "STF Armature"))
	blender_armature.stf_id = stf_id
	if(json_resource.get("name")):
		blender_armature.stf_name = json_resource["name"]
		blender_armature.stf_name_source_of_truth = True

	tmp_hook_object: bpy.types.Object = bpy.data.objects.new("TRASH", blender_armature)
	bpy.context.scene.collection.objects.link(tmp_hook_object)
	def _clean_tmp_mesh_object():
		bpy.data.objects.remove(tmp_hook_object)
	context.add_task(_clean_tmp_mesh_object)

	for bone_id in json_resource.get("root_bones", []):
		context.import_resource(bone_id, tmp_hook_object)

	return blender_armature


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_armature: bpy.types.Armature = application_object
	ensure_stf_id(context, blender_armature)

	tmp_hook_object: bpy.types.Object = bpy.data.objects.new("TRASH", blender_armature)
	bpy.context.scene.collection.objects.link(tmp_hook_object)
	def _clean_tmp_mesh_object():
		bpy.data.objects.remove(tmp_hook_object)
	context.add_task(_clean_tmp_mesh_object)

	root_bones = []
	ret = {
		"type": _stf_type,
		"name": blender_armature.stf_name if blender_armature.stf_name_source_of_truth else blender_armature.name,
		"root_bones": root_bones,
	}

	root_bone_definitions = []
	for blender_bone in blender_armature.bones:
		if(blender_bone.parent == None):
			root_bone_definitions.append(ArmatureBone(blender_armature, blender_bone.name))

	for root_bone_definition in root_bone_definitions:
		root_bones.append(context.serialize_resource(root_bone_definition, context_object=tmp_hook_object))

	return ret, blender_armature.stf_id


class STF_Module_STF_Armature(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["armature", "prefab"]
	understood_application_types = [bpy.types.Armature]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Armature
]


def register():
	boilerplate_register(bpy.types.Armature, "data")

def unregister():
	boilerplate_unregister(bpy.types.Armature, "data")
