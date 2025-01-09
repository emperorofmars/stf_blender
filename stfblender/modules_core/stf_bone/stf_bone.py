import bpy
import mathutils

from ....libstf.stf_report import STF_Report_Severity, STFReport
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_object_to_trs, to_trs, trs_to_blender_object
from ..stf_armature.stf_armature import STF_BlenderBoneExportContext, STF_BlenderBoneImportContext


_stf_type = "stf.bone"


def _stf_import(context: STF_BlenderBoneImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> any:
	blender_armature: bpy.types.Armature = parent_application_object

	if(bpy.context.mode != "OBJECT"): bpy.ops.object.mode_set(mode="OBJECT")
	bpy.context.view_layer.objects.active = blender_armature
	bpy.ops.object.mode_set(mode="EDIT")

	blender_bone = blender_armature.edit_bones.new(json_resource.get("name", "STF Bone"))

	bpy.ops.object.mode_set(mode="OBJECT")

	"""if(import_hook_results and len(import_hook_results) == 1):
		blender_object: bpy.types.Bone = import_hook_results[0]
		blender_object.name = json_resource.get("name", "STF Bone")
	else:
		blender_object: bpy.types.Bone = bpy.data.objects.new(json_resource.get("name", "STF Bone"), None)
	blender_object.stf_id = id
	blender_object.stf_name = json_resource.get("name", "")
	parent_application_object.objects.link(blender_object)

	if(import_hook_results and len(import_hook_results) > 1):
		for hook_result in import_hook_results:
			hook_result.stf_is_component_stand_in = True
			hook_result.parent = blender_object
			parent_application_object.objects.link(hook_result)"""

	#trs_to_blender_object(json_resource["trs"], blender_object)

	"""for child_id in json_resource.get("children", []):
		child: bpy.types.Bone = context.import_resource(child_id)
		if(child):
			child.parent_type = "Bone"
			child.parent = blender_object
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STF_Report_Severity.Error, id, _stf_type, blender_object))"""
	return blender_bone


def _stf_export(context: STF_BlenderBoneExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_bone: bpy.types.Bone = application_object
	ensure_stf_id(blender_bone)

	children = []
	for child in blender_bone.children:
		children.append(context.serialize_resource(child))

	bone = {
		"type": _stf_type,
		"name": blender_bone.stf_name if blender_bone.stf_name else blender_bone.name,
		#"trs": to_trs(blender_bone.head, blender_bone.matrix_local),
		"children": children,
	}

	return bone, blender_bone.stf_id, context


class STF_Module_STF_Bone(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["bone", "node"]
	understood_application_types = [bpy.types.Bone]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Bone
]


def register():
	bpy.types.Bone.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Bone.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Bone.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Bone.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Bone, "stf_id"):
		del bpy.types.Bone.stf_id
	if hasattr(bpy.types.Bone, "stf_name"):
		del bpy.types.Bone.stf_name
	if hasattr(bpy.types.Bone, "stf_components"):
		del bpy.types.Bone.stf_components
	if hasattr(bpy.types.Bone, "stf_active_component_index"):
		del bpy.types.Bone.stf_active_component_index
