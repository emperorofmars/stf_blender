from typing import Callable
import bpy
import mathutils
import math

from ....importer.stf_import_context import STF_ImportContext
from ....exporter.stf_export_context import STF_ExportContext
from ....utils.armature_bone import ArmatureBone
from ....utils.animation_conversion_utils import *


def _create_translation_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Vector()
	# In Blender, bones get animated relative to their own rest pose. In STF, bones are animated relative to their parent.
	if(blender_object.get_bone().parent):
		offset = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).translation
	else:
		offset = blender_object.get_bone().matrix_local.translation

	def _ret(value: list[float]) -> float:
		value = [value[i] + offset[i] for i in range(len(value))]
		return convert_bone_translation_to_stf(value)
	return _ret

def _create_rotation_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Quaternion()
	# In Blender, bones get animated relative to their own rest pose. In STF, bones are animated relative to their parent.
	if(blender_object.get_bone().parent):
		_, offset, _ = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).decompose()
	else:
		_, offset, _ = blender_object.get_bone().matrix_local.decompose()

	def _ret(value: list[float]) -> float:
		value = mathutils.Quaternion(value)
		return convert_bone_rotation_to_stf((value @ offset)[:])
	return _ret

def _create_rotation_euler_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Quaternion()
	# In Blender, bones get animated relative to their own rest pose. In STF, bones are animated relative to their parent.
	if(blender_object.get_bone().parent):
		_, offset, _ = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).decompose()
	else:
		_, offset, _ = (blender_object.get_bone().matrix_local @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")).decompose()

	def _ret(value: list[float]) -> float:
		value = mathutils.Euler(value).to_quaternion()
		value = (value @ offset).to_euler()
		return convert_bone_rotation_euler_to_stf(value[:])
	return _ret


def _create_scale_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Vector()
	# In Blender, bones get animated relative to their own rest pose. In STF, bones are animated relative to their parent.
	if(blender_object.get_bone().parent):
		_, _, offset = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).decompose()
	else:
		_, _, offset = blender_object.get_bone().matrix_local.decompose()

	def _ret(value: list[float]) -> float:
		value = [value[i] * offset[i] for i in range(len(value))]
		return convert_bone_scale_to_stf(value)
	return _ret


def resolve_property_path_to_stf_func(context: STF_ExportContext, blender_object: ArmatureBone, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[list[float]], list[float]], list[int]]:
	import re
	if(match := re.search(r"^location", data_path)):
		return [blender_object.get_bone().stf_info.stf_id, "t"], _create_translation_to_stf_func(blender_object), translation_bone_index_conversion_to_stf

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [blender_object.get_bone().stf_info.stf_id, "r"], _create_rotation_to_stf_func(blender_object), rotation_bone_index_conversion_to_stf

	if(match := re.search(r"^rotation_euler", data_path)):
		return [blender_object.get_bone().stf_info.stf_id, "r_euler"], _create_rotation_euler_to_stf_func(blender_object), rotation_euler_bone_index_conversion_to_stf

	if(match := re.search(r"^scale", data_path)):
		return [blender_object.get_bone().stf_info.stf_id, "s"], _create_scale_to_stf_func(blender_object), scale_bone_index_conversion_to_stf

	return None


def resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	if(type(blender_object) is ArmatureBone):
		blender_object = blender_object.armature.bones[blender_object.name]
	match(stf_path[1]):
		case "t":
			return None, 0, "OBJECT", "pose.bones[\"" + blender_object.name + "\"].location", translation_bone_index_conversion_to_blender, convert_bone_translation_to_blender
		case "r":
			return None, 0, "OBJECT", "pose.bones[\"" + blender_object.name + "\"].rotation_quaternion", rotation_index_bone_conversion_to_blender, convert_bone_rotation_to_blender
		case "r_euler":
			return None, 0, "OBJECT", "pose.bones[\"" + blender_object.name + "\"].rotation_euler", rotation_euler_bone_index_conversion_to_blender, convert_bone_rotation_euler_to_blender
		case "s":
			return None, 0, "OBJECT", "pose.bones[\"" + blender_object.name + "\"].scale", scale_bone_index_conversion_to_blender, convert_bone_scale_to_blender
		case "components":
			return context.resolve_stf_property_path(stf_path[2:], application_object)
		case "component_mods":
			return context.resolve_stf_property_path(stf_path[2:], application_object)

	return None