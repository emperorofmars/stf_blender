from typing import Callable
import mathutils
import math

from ....importer.stf_import_context import STF_ImportContext
from ....exporter.stf_export_context import STF_ExportContext
from ....utils.armature_bone import ArmatureBone
from ....utils.animation_conversion_utils import *
from ....base.property_path_part import BlenderPropertyPathPart, STFPropertyPathPart


# In Blender, bones get animated relative to their own rest pose.
# In STF, bones are animated relative to their parent.
# At least Blenders values are consistent here.

"""
Export
"""

def _create_translation_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Vector()
	if(blender_object.get_bone().parent):
		offset = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).translation
	else:
		offset = (mathutils.Matrix.Rotation(math.radians(-90), 4, "X") @ blender_object.get_bone().matrix_local).translation

	def _ret(value: list[float]) -> float:
		value = [value[i] + offset[i] for i in range(len(value))]
		return convert_bone_translation_to_stf(value)
	return _ret

def _create_rotation_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Quaternion()
	if(blender_object.get_bone().parent):
		_, offset, _ = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).decompose()
	else:
		_, offset, _ = (blender_object.get_bone().matrix_local @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")).decompose()

	def _ret(value: list[float]) -> float:
		value = mathutils.Quaternion(value)
		return convert_bone_rotation_to_stf((value @ offset)[:])
	return _ret

def _create_rotation_euler_to_stf_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Quaternion()
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
	if(blender_object.get_bone().parent):
		_, _, offset = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).decompose()
	else:
		_, _, offset = blender_object.get_bone().matrix_local.decompose()

	def _ret(value: list[float]) -> float:
		value = [value[i] * offset[i] for i in range(len(value))]
		return convert_bone_scale_to_stf(value)
	return _ret


def resolve_property_path_to_stf_func(context: STF_ExportContext, blender_object: ArmatureBone, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	import re

	has_constraints = False
	for obj in context.get_root().all_objects[:]:
		if(obj.data and obj.data == blender_object.armature):
			if(len(obj.pose.bones[blender_object.name].constraints) > 0):
				has_constraints = True
				break
			for bone in obj.pose.bones:
				if(len(bone.constraints) > 0):
					for constraint in bone.constraints:
						if(constraint.type == "IK"):
							if(constraint.target == obj and constraint.subtarget == blender_object.name):
								has_constraints = True
								break
				if(has_constraints): break
		if(has_constraints): break


	if(match := re.search(r"^location", data_path)):
		return STFPropertyPathPart([blender_object.get_bone().stf_info.stf_id, "t"], _create_translation_to_stf_func(blender_object), translation_bone_index_conversion_to_stf, has_constraints)

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return STFPropertyPathPart([blender_object.get_bone().stf_info.stf_id, "r"], _create_rotation_to_stf_func(blender_object), rotation_bone_index_conversion_to_stf, has_constraints)

	if(match := re.search(r"^rotation_euler", data_path)):
		return STFPropertyPathPart([blender_object.get_bone().stf_info.stf_id, "r_euler"], _create_rotation_euler_to_stf_func(blender_object), rotation_euler_bone_index_conversion_to_stf, has_constraints)

	if(match := re.search(r"^scale", data_path)):
		return STFPropertyPathPart([blender_object.get_bone().stf_info.stf_id, "s"], _create_scale_to_stf_func(blender_object), scale_bone_index_conversion_to_stf, has_constraints)

	return None


"""
Import
"""

def _create_translation_to_blender_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Vector()
	if(blender_object.get_bone().parent):
		offset = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).translation
	else:
		offset = (mathutils.Matrix.Rotation(math.radians(-90), 4, "X") @ blender_object.get_bone().matrix_local).translation

	def _ret(value: list[float]) -> float:
		value = convert_bone_translation_to_blender(value)
		return [value[i] - offset[i] for i in range(len(value))]
		#return convert_bone_translation_to_blender(value)
	return _ret

def _create_rotation_to_blender_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Quaternion()
	if(blender_object.get_bone().parent):
		_, offset, _ = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).inverted_safe().decompose()
	else:
		_, offset, _ = (blender_object.get_bone().matrix_local @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")).inverted_safe().decompose()

	def _ret(value: list[float]) -> float:
		value = mathutils.Quaternion(convert_bone_rotation_to_blender(value))
		return (value @ offset)[:]
	return _ret

def _create_rotation_euler_to_blender_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Quaternion()
	if(blender_object.get_bone().parent):
		_, offset, _ = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).inverted_safe().decompose()
	else:
		_, offset, _ = (blender_object.get_bone().matrix_local @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")).inverted_safe().decompose()

	def _ret(value: list[float]) -> float:
		value = mathutils.Euler(convert_bone_rotation_euler_to_blender(value)).to_quaternion()
		return (value @ offset).to_euler()[:]
	return _ret

def _create_scale_to_blender_func(blender_object: ArmatureBone) -> Callable:
	offset = mathutils.Vector()
	if(blender_object.get_bone().parent):
		_, _, offset = (blender_object.get_bone().parent.matrix_local.inverted_safe() @ blender_object.get_bone().matrix_local).inverted_safe().decompose()
	else:
		_, _, offset = blender_object.get_bone().matrix_local.inverted_safe().decompose()

	def _ret(value: list[float]) -> float:
		value = convert_bone_scale_to_blender(value)
		return [value[i] * offset[i] for i in range(len(value))]
	return _ret


def resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> BlenderPropertyPathPart:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "t":
			return BlenderPropertyPathPart("OBJECT", "pose.bones[\"" + blender_object.name + "\"].location", _create_translation_to_blender_func(blender_object), translation_bone_index_conversion_to_blender)
		case "r":
			return BlenderPropertyPathPart("OBJECT", "pose.bones[\"" + blender_object.name + "\"].rotation_quaternion", _create_rotation_to_blender_func(blender_object), rotation_index_bone_conversion_to_blender)
		case "r_euler":
			return BlenderPropertyPathPart("OBJECT", "pose.bones[\"" + blender_object.name + "\"].rotation_euler", _create_rotation_euler_to_blender_func(blender_object), rotation_euler_bone_index_conversion_to_blender)
		case "s":
			return BlenderPropertyPathPart("OBJECT", "pose.bones[\"" + blender_object.name + "\"].scale", _create_scale_to_blender_func(blender_object), scale_bone_index_conversion_to_blender)
		case "components":
			return context.resolve_stf_property_path(stf_path[2:], application_object)
		case "component_mods":
			return context.resolve_stf_property_path(stf_path[2:], application_object)

	return None
