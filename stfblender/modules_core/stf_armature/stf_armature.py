import bpy

from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.armature_bone import ArmatureBone
from ...utils.id_binding_resolver import STF_Blender_BindingResolver


_stf_type = "stf.armature"


class STF_BlenderBoneExportContext(STF_ResourceExportContext):
	def ensure_resource_properties(self):
		super().ensure_resource_properties()
		if(not hasattr(self._json_resource, "bones")):
			self._json_resource["bones"] = {}

	def id_exists(self, id: str) -> bool:
		if(id in self._json_resource["bones"]): return True
		else: return super().id_exists(id)

	def get_resource_id(self, application_object: any) -> str | None:
		if(type(application_object) is ArmatureBone):
			bone = application_object.armature.bones[application_object.name]
			if(bone.stf_id and bone.stf_id in self._json_resource["bones"]):
				return bone.stf_id
			else:
				return None
		else:
			return super().get_resource_id(application_object)

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		if(type(application_object) is ArmatureBone):
			self._json_resource["bones"][id] = json_resource
		else:
			super().register_serialized_resource(application_object, json_resource, id)


class STF_BlenderBoneImportContext(STF_ResourceImportContext):
	def __init__(self, parent_context, json_resource, parent_application_object):
		super().__init__(parent_context, json_resource, parent_application_object)

	def get_json_resource(self, id: str) -> dict:
		if(id in self._json_resource["bones"]):
			return self._json_resource["bones"][id]
		else:
			return super().get_json_resource(id)


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_armature = bpy.data.armatures.new(json_resource.get("name", "STF Armature"))
	blender_armature.stf_id = id
	blender_armature.stf_name = json_resource.get("name")

	hook_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_armature)
	bpy.context.scene.collection.objects.link(hook_object)

	bone_import_context = STF_BlenderBoneImportContext(context, json_resource, hook_object)
	for bone_id in json_resource.get("root_bones", []):
		bone_import_context.import_resource(bone_id)

	bpy.data.objects.remove(hook_object)

	return blender_armature, bone_import_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_armature: bpy.types.Armature = application_object
	ensure_stf_id(context, blender_armature)
	blender_armature_object: bpy.types.Object = parent_application_object

	root_bones = []
	ret = {
		"type": _stf_type,
		"root_bones": root_bones,
	}

	bone_export_context = STF_BlenderBoneExportContext(context, ret, blender_armature_object)
	root_bone_definitions = []
	for blender_bone in blender_armature.bones:
		if(blender_bone.parent == None):
			root_bone_definitions.append(ArmatureBone(blender_armature, blender_bone.name))

	for root_bone_definition in root_bone_definitions:
		root_bones.append(bone_export_context.serialize_resource(root_bone_definition))

	return ret, blender_armature.stf_id, bone_export_context


def _resolve_id_binding_func(blender_object: any, id: str) -> any:
	armature: bpy.types.Armature = blender_object
	for bone in armature.bones:
		if(bone.stf_id == id):
			return bone
	return None


class STF_Module_STF_Armature(STF_Blender_BindingResolver, STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["armature", "prefab"]
	understood_application_types = [bpy.types.Armature]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object

	target_blender_binding_types = [bpy.types.Armature]
	resolve_id_binding_func = _resolve_id_binding_func


register_stf_modules = [
	STF_Module_STF_Armature
]


def register():
	bpy.types.Armature.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Armature.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Armature.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Armature.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Armature, "stf_id"):
		del bpy.types.Armature.stf_id
	if hasattr(bpy.types.Armature, "stf_name"):
		del bpy.types.Armature.stf_name
	if hasattr(bpy.types.Armature, "stf_components"):
		del bpy.types.Armature.stf_components
	if hasattr(bpy.types.Armature, "stf_active_component_index"):
		del bpy.types.Armature.stf_active_component_index
