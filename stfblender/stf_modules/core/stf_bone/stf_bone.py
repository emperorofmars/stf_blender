import bpy
import mathutils
import math

from ....base.stf_report import STFReportSeverity, STFReport
from ....base.stf_module import STF_Module
from ....importer.stf_import_context import STF_ImportContext
from ....exporter.stf_export_context import STF_ExportContext
from ....utils.component_utils import get_components_from_object
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister
from ....utils.id_utils import ensure_stf_id
from ....utils import trs_utils
from ....utils.armature_bone import ArmatureBone
from ....utils.animation_conversion_utils import *
from .stf_bone_property_conversion import resolve_property_path_to_stf_func, resolve_stf_property_to_blender_func


_stf_type = "stf.bone"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_armature: bpy.types.Armature = context_object.data
	blender_object: bpy.types.Object = context_object

	# Once Blender enters into edit-mode, the Bone references will be invalidated. Store the child-names as string.
	children = []
	for child_id in json_resource.get("children", []):
		child: ArmatureBone = context.import_resource(child_id, context_object, "node")
		if(child):
			children.append(child.name)
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STFReportSeverity.Error, stf_id, _stf_type, blender_object))

	if(bpy.context.mode != "OBJECT"): bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
	bpy.context.view_layer.objects.active = blender_object
	bpy.ops.object.mode_set(mode="EDIT", toggle=False)

	blender_edit_bone = blender_armature.edit_bones.new(json_resource.get("name", "STF Bone"))
	blender_bone_name = blender_edit_bone.name

	blender_edit_bone.head = mathutils.Vector([0, 0, 0])
	blender_edit_bone.tail = mathutils.Vector([0, 0, 1])
	blender_edit_bone.roll = 0

	blender_edit_bone.matrix = mathutils.Matrix.LocRotScale(trs_utils.stf_translation_to_blender(json_resource["translation"]), trs_utils.stf_rotation_to_blender(json_resource["rotation"]), mathutils.Vector([1, 1, 1])) @ mathutils.Matrix.Rotation(math.radians(90), 4, "X")
	blender_edit_bone.length = json_resource["length"]

	if("connected" in json_resource): blender_edit_bone.use_connect = json_resource["connected"]

	for child_name in children:
		child = blender_armature.edit_bones[child_name]
		child.parent = blender_edit_bone

	bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

	blender_bone = ArmatureBone(blender_armature, blender_bone_name)

	context.register_imported_resource(stf_id, blender_bone)

	blender_armature.bones[blender_bone_name].stf_info.stf_id = stf_id
	if(json_resource.get("name")):
		blender_armature.bones[blender_bone_name].stf_info.stf_name = json_resource["name"]
		blender_armature.bones[blender_bone_name].stf_info.stf_name_source_of_truth = True

	return blender_bone


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_bone_def: ArmatureBone = application_object
	ensure_stf_id(context, blender_bone_def.get_bone(), blender_bone_def.get_bone().stf_info)

	blender_armature: bpy.types.Armature = context_object

	# Once Blender enters into edit-mode, the Bone reference will be invalidated. Access by name instead.
	blender_bone_name = blender_bone_def.name
	blender_child_bones = [ArmatureBone(blender_armature, child.name) for child in blender_bone_def.get_bone().children]
	stf_id = blender_bone_def.get_bone().stf_info.stf_id

	children = []
	ret = {
		"type": _stf_type,
		"name": blender_bone_def.get_bone().stf_info.stf_name if blender_bone_def.get_bone().stf_info.stf_name_source_of_truth else blender_bone_def.get_bone().name,
		"children": children,
	}
	if(blender_armature.bones[blender_bone_name].parent):
		ret["connected"] = blender_armature.bones[blender_bone_name].use_connect

	for child in blender_child_bones:
		children.append(context.serialize_resource(child, context_object, "node"))

	blender_bone: bpy.types.Bone = blender_armature.bones[blender_bone_name]

	t, r, _ = (blender_bone.matrix_local @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")).decompose()

	ret["translation"] = trs_utils.blender_translation_to_stf(t)
	ret["rotation"] = trs_utils.blender_rotation_to_stf(r)
	ret["length"] = blender_bone.length

	return ret, stf_id


def _get_components_from_object(application_object: ArmatureBone) -> list:
	return get_components_from_object(application_object.get_bone())

def _get_components_holder_func(application_object: ArmatureBone) -> any:
	return application_object.get_bone()


class STF_Module_STF_Bone(STF_Module):
	stf_type = _stf_type
	stf_kind = "node"
	like_types = ["bone", "node"]
	understood_application_types = [ArmatureBone]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = _get_components_from_object
	get_components_holder_func = _get_components_holder_func

	understood_application_property_path_types = [ArmatureBone]
	understood_application_property_path_parts = ["location", "rotation_quaternion", "rotation_euler", "scale"]
	resolve_property_path_to_stf_func = resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Bone
]


def register():
	boilerplate_register(bpy.types.Bone, "node")

def unregister():
	boilerplate_unregister(bpy.types.Bone, "node")
