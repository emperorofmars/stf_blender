import bpy

from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.armature"


class STF_BlenderBoneExportContext(STF_ResourceExportContext):
	def ensure_resource_properties(self):
		super().ensure_resource_properties()
		if(not hasattr(self._json_resource, "bones")):
			self._json_resource["bones"] = {}

	def get_resource_id(self, application_object: any) -> str | None:
		if(type(application_object) is bpy.types.Bone):
			if(application_object.stf_id and application_object.stf_id in self._json_resource["bones"].keys()):
				return application_object.stf_id
			else:
				return None
		else:
			return super().get_resource_id(application_object)

	def register_serialized_resource(self, application_object: any, json_resource: dict, id: str):
		if(type(application_object) is bpy.types.Bone):
			self._json_resource["bones"][id] = json_resource
		else:
			super().register_serialized_resource(application_object, json_resource, id)


class STF_BlenderBoneImportContext(STF_ResourceImportContext):
	def get_json_resource(self, id: str) -> dict:
		if(id in self._json_resource["bones"]):
			return self._json_resource["bones"][id]
		else:
			return super().get_json_resource(id)


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> any:
	armature = bpy.data.armatures.new(json_resource.get("name", "STF Armature"))
	armature.stf_id = id
	armature.stf_name = json_resource.get("name", "")

	node_import_context = STF_BlenderBoneImportContext(context, json_resource, armature)
	for bone_id in json_resource.get("root_bones", []):
		node_import_context.import_resource(bone_id)

	return armature


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	armature: bpy.types.Armature = application_object
	ensure_stf_id(armature)

	root_bones = []
	ret = {
		"type": _stf_type,
		"name": armature.stf_name if armature.stf_name else armature.name,
		"root_bones": root_bones,
	}

	bone_export_context = STF_BlenderBoneExportContext(context, ret)
	for blender_bone in armature.bones:
		if(blender_bone.parent == None):
			root_bones.append(bone_export_context.serialize_resource(blender_bone))

	return ret, armature.stf_id, bone_export_context


class STF_Module_STF_Armature(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["prefab", "armature"]
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
