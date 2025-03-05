import bpy

from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.armature_bone import ArmatureBone
from ...utils.id_binding_resolver import STF_Blender_BindingResolver


_stf_type = "stf.armature"


def _stf_import(context: STF_RootImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
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

	bone_import_context = STF_ResourceImportContext(context, json_resource, tmp_hook_object)
	for bone_id in json_resource.get("root_bones", []):
		bone_import_context.import_resource(bone_id)

	return blender_armature, bone_import_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
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

	bone_export_context = STF_ResourceExportContext(context, ret, tmp_hook_object)
	root_bone_definitions = []
	for blender_bone in blender_armature.bones:
		if(blender_bone.parent == None):
			root_bone_definitions.append(ArmatureBone(blender_armature, blender_bone.name))

	for root_bone_definition in root_bone_definitions:
		root_bones.append(bone_export_context.serialize_resource(root_bone_definition))

	return ret, blender_armature.stf_id, bone_export_context


class STF_Module_STF_Armature(STF_Blender_BindingResolver, STF_Module):
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
	bpy.types.Armature.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Armature.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Armature.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Armature.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Armature.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Armature, "stf_id"):
		del bpy.types.Armature.stf_id
	if hasattr(bpy.types.Armature, "stf_name"):
		del bpy.types.Armature.stf_name
	if hasattr(bpy.types.Armature, "stf_name_source_of_truth"):
		del bpy.types.Armature.stf_name_source_of_truth
	if hasattr(bpy.types.Armature, "stf_components"):
		del bpy.types.Armature.stf_components
	if hasattr(bpy.types.Armature, "stf_active_component_index"):
		del bpy.types.Armature.stf_active_component_index
