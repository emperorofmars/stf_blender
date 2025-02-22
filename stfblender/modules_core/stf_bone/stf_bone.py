import bpy


from ....libstf.stf_report import STFReportSeverity, STFReport
from ....libstf.stf_module import STF_Module
from ....libstf.stf_import_context import STF_ResourceImportContext
from ....libstf.stf_export_context import STF_ResourceExportContext
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils import trs_utils
from ...utils.armature_bone import ArmatureBone


_stf_type = "stf.bone"


def _stf_import(context: STF_ResourceImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_armature: bpy.types.Armature = parent_application_object.data
	blender_object: bpy.types.Object = parent_application_object

	# Once Blender enters into edit-mode, the Bone references will be invalidated. Store the child-names as string.
	children = []
	for child_id in json_resource.get("children", []):
		child: ArmatureBone = context.import_resource(child_id)
		if(child):
			children.append(child.name)
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, stf_id, _stf_type, blender_object))

	if(bpy.context.mode != "OBJECT"): bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
	bpy.context.view_layer.objects.active = blender_object
	bpy.ops.object.mode_set(mode="EDIT", toggle=False)

	blender_edit_bone = blender_armature.edit_bones.new(json_resource.get("name", "STF Bone"))
	blender_bone_name = blender_edit_bone.name

	blender_edit_bone.head = trs_utils.stf_translation_to_blender(json_resource["head"])
	blender_edit_bone.tail = trs_utils.stf_translation_to_blender(json_resource["tail"])
	blender_edit_bone.roll = json_resource["roll"]

	if("connected" in json_resource): blender_edit_bone.use_connect = json_resource["connected"]

	for child_name in children:
		child = blender_armature.edit_bones[child_name]
		child.parent = blender_edit_bone

	bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

	blender_bone = ArmatureBone(blender_armature, blender_bone_name)
	bone_context = STF_ResourceImportContext(context, json_resource, blender_bone)
	context.register_imported_resource(stf_id, blender_bone)

	blender_armature.bones[blender_bone_name].stf_id = stf_id
	if(json_resource.get("name")):
		blender_armature.bones[blender_bone_name].stf_name = json_resource["name"]
		blender_armature.bones[blender_bone_name].stf_name_source_of_truth = True

	return blender_bone, bone_context


def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_bone_def: ArmatureBone = application_object
	ensure_stf_id(context, blender_bone_def.get_bone())

	blender_armature_object: bpy.types.Object = parent_application_object
	blender_armature: bpy.types.Armature = parent_application_object.data

	# Once Blender enters into edit-mode, the Bone reference will be invalidated. Access by name instead.
	blender_bone_name = blender_bone_def.name
	blender_child_bones = [ArmatureBone(blender_armature, child.name) for child in blender_bone_def.get_bone().children]
	stf_id = blender_bone_def.get_bone().stf_id

	children = []
	ret = {
		"type": _stf_type,
		"name": blender_bone_def.get_bone().stf_name if blender_bone_def.get_bone().stf_name_source_of_truth else blender_bone_def.get_bone().name,
		"children": children,
	}
	if(blender_armature.bones[blender_bone_name].parent):
		ret["connected"] = blender_armature.bones[blender_bone_name].use_connect

	for child in blender_child_bones:
		children.append(context.serialize_resource(child))

	if(bpy.context.mode != "OBJECT"): bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
	bpy.context.view_layer.objects.active = blender_armature_object
	bpy.ops.object.mode_set(mode="EDIT", toggle=False)

	edit_bone = blender_armature.edit_bones[blender_bone_name]

	ret["head"] = trs_utils.blender_translation_to_stf(edit_bone.head)
	ret["tail"] = trs_utils.blender_translation_to_stf(edit_bone.tail)
	ret["roll"] = edit_bone.roll

	bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

	return ret, stf_id, context


class STF_Module_STF_Bone(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["bone", "node"]
	understood_application_types = [ArmatureBone]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Bone
]


def register():
	bpy.types.Bone.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Bone.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Bone.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Bone.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Bone.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Bone, "stf_id"):
		del bpy.types.Bone.stf_id
	if hasattr(bpy.types.Bone, "stf_name"):
		del bpy.types.Bone.stf_name
	if hasattr(bpy.types.Bone, "stf_name_source_of_truth"):
		del bpy.types.Bone.stf_name_source_of_truth
	if hasattr(bpy.types.Bone, "stf_components"):
		del bpy.types.Bone.stf_components
	if hasattr(bpy.types.Bone, "stf_active_component_index"):
		del bpy.types.Bone.stf_active_component_index
