import math
import re
import mathutils
from typing import Callable

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.animation_conversion_utils import *


"""
Export
"""

def _create_translation_to_stf_func(blender_object: bpy.types.Object) -> Callable:
	# The animated value is the 'location'. Unfortunately, there is a very good chance it is complete bullshit, with (0, 0, 0) being a completely random point, not at the world origin or the parent.
	# This is due to the 'parent_matrix_inverse'. It should be a computed value, as should be the 'location'. The animated property here should be consistent in relation to something, be it the world origin or parent.
	# Blender why?

	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		offset = blender_object.matrix_parent_inverse.copy()

		def _ret(value: list[float]) -> float:
			return convert_translation_to_stf((offset @ mathutils.Matrix.Translation(value)).translation)
		return _ret

	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		pose_bone = blender_object.parent.pose.bones[blender_object.parent_bone]
		offset = mathutils.Matrix.Translation([0, 0, (pose_bone.tail - pose_bone.head).length]) @ mathutils.Matrix.Rotation(math.radians(90), 4, "X") @ blender_object.matrix_parent_inverse

		def _ret(value: list[float]) -> float:
			return convert_translation_to_stf((offset @ mathutils.Matrix.Translation(value)).translation)
		return _ret

	else:
		return convert_translation_to_stf


def _convert_bone_offset_rotation_to_stf(blender_object: bpy.types.Object) -> mathutils.Matrix:
	return mathutils.Matrix.Rotation(math.radians(90), 4, "X") @ blender_object.matrix_parent_inverse

def _create_rotation_to_stf_func(blender_object: bpy.types.Object) -> Callable:
	# The animated value is the 'rotation_quaternion'. Unfortunately, there is a very good chance it is complete bullshit, with identity being a completely random orientation, not relative to the world origin or the parent.
	# This is due to the 'parent_matrix_inverse'. It should be a computed value, as should be the 'rotation_quaternion'. The animated property here should be consistent in relation to something, be it the world origin or parent.
	# Blender why?

	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		offset = blender_object.matrix_parent_inverse.copy()

		def _ret(value: list[float]) -> float:
			return convert_rotation_to_stf((offset @ mathutils.Quaternion(value).to_matrix().to_4x4()).to_quaternion())
		return _ret

	# todo figure this out for bone parents
	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		offset = _convert_bone_offset_rotation_to_stf(blender_object)

		def _ret(value: list[float]) -> float:
			return convert_rotation_to_stf((offset @ mathutils.Quaternion(value).to_matrix().to_4x4()).to_quaternion())
		return _ret

	else:
		return convert_rotation_to_stf

def _create_rotation_euler_to_stf_func(blender_object: bpy.types.Object) -> Callable:
	# The animated value is the 'rotation_euler'. Unfortunately, there is a very good chance it is complete bullshit, with identity being a completely random orientation, not relative to the world origin or the parent.
	# This is due to the 'parent_matrix_inverse'. It should be a computed value, as should be the 'rotation_euler'. The animated property here should be consistent in relation to something, be it the world origin or parent.
	# Blender why?

	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		offset = blender_object.matrix_parent_inverse.copy()

		def _ret(value: list[float]) -> float:
			return convert_rotation_euler_to_stf((offset @ mathutils.Euler(value).to_matrix().to_4x4()).to_euler())
		return _ret

	# todo figure this out for bone parents
	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		offset = _convert_bone_offset_rotation_to_stf(blender_object)

		def _ret(value: list[float]) -> float:
			return convert_rotation_euler_to_stf((offset @ mathutils.Euler(value).to_matrix().to_4x4()).to_euler())
		return _ret

	else:
		return convert_rotation_euler_to_stf

def _create_scale_to_stf_func(blender_object: bpy.types.Object) -> Callable:
	# The animated value is the 'scale'. Unfortunately, there is a very good chance it is complete bullshit, with (1, 1, 1) being a completely random size, be it relative to the world or the parent.
	# This is due to the 'parent_matrix_inverse'. It should be a computed value, as should be the 'scale'. The animated property here should be consistent in relation to something, be it the world origin or parent.
	# Blender why?

	offset = mathutils.Vector([1, 1, 1])
	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		_, _, s = (blender_object.parent.matrix_world.inverted_safe() @ blender_object.matrix_world).decompose()
		offset = [s[i] / blender_object.scale[i] for i in range(3)]

	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		_, _, s = ((blender_object.parent.matrix_world @ (blender_object.parent.pose.bones[blender_object.parent_bone].matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X"))).inverted_safe() @ blender_object.matrix_world).decompose() # Blender why
		offset = [s[i] / blender_object.scale[i] for i in range(3)]

	def _ret(value: list[float]) -> float:
		value = [value[i] * offset[i] for i in range(3)]
		return convert_scale_to_stf(value)
	return _ret


def stf_node_resolve_property_path_to_stf_func(context: STF_ExportContext, blender_object: bpy.types.Object, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[list[float]], list[float]], list[int]]:
	if(match := re.search(r"^location", data_path)):
		return [blender_object.stf_info.stf_id, "t"], _create_translation_to_stf_func(blender_object), translation_index_conversion_to_stf

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [blender_object.stf_info.stf_id, "r"], _create_rotation_to_stf_func(blender_object), rotation_index_conversion_to_stf

	if(match := re.search(r"^rotation_euler", data_path)):
		return [blender_object.stf_info.stf_id, "r_euler"], _create_rotation_euler_to_stf_func(blender_object), rotation_euler_index_conversion_to_stf

	if(match := re.search(r"^scale", data_path)):
		return [blender_object.stf_info.stf_id, "s"], _create_scale_to_stf_func(blender_object), scale_index_conversion_to_stf

	if(match := re.search(r"^hide_render", data_path)):
		return [blender_object.stf_info.stf_id, "enabled"], lambda v: [not v[0]], None

	return None


"""
Import
"""

def _create_translation_to_blender_func(blender_object: bpy.types.Object) -> Callable:
	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		parent_mat = blender_object.parent.matrix_world.copy()

		def _ret(value: list[float]) -> float:
			value = convert_translation_to_blender(value)
			return (parent_mat @ mathutils.Matrix.Translation(value)).translation
		return _ret

	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		pose_bone = blender_object.parent.pose.bones[blender_object.parent_bone]
		parent_mat = blender_object.parent.matrix_world @ pose_bone.matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")

		def _ret(value: list[float]) -> float:
			value = convert_translation_to_blender(value)
			return (parent_mat @ mathutils.Matrix.Translation(value)).translation
		return _ret
	
	else:
		return convert_translation_to_blender

def _convert_bone_offset_rotation_to_blender(blender_object: bpy.types.Object) -> mathutils.Matrix:
	pose_bone = blender_object.parent.pose.bones[blender_object.parent_bone]
	return blender_object.parent.matrix_world @ pose_bone.matrix @ mathutils.Matrix.Rotation(math.radians(-90), 4, "X")

def _create_rotation_to_blender_func(blender_object: bpy.types.Object) -> Callable:
	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		parent_mat = blender_object.parent.matrix_world.copy()

		def _ret(value: list[float]) -> float:
			value = convert_rotation_to_blender(value).to_matrix().to_4x4()
			return (parent_mat @ value).to_quaternion()
		return _ret

	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		parent_mat = _convert_bone_offset_rotation_to_blender(blender_object)

		def _ret(value: list[float]) -> float:
			value = convert_rotation_to_blender(value).to_matrix().to_4x4()
			return (parent_mat @ value).to_quaternion()
		return _ret
	
	else:
		return convert_rotation_to_blender

def _create_rotation_euler_to_blender_func(blender_object: bpy.types.Object) -> Callable:
	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		parent_mat = blender_object.parent.matrix_world.copy()

		def _ret(value: list[float]) -> float:
			value = mathutils.Euler(convert_rotation_euler_to_blender(value)).to_matrix().to_4x4()
			return (parent_mat @ value).to_euler()
		return _ret

	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		parent_mat = _convert_bone_offset_rotation_to_blender(blender_object) # blender_object.parent.matrix_world.copy()

		def _ret(value: list[float]) -> float:
			value = mathutils.Euler(convert_rotation_euler_to_blender(value)).to_matrix().to_4x4()
			return (parent_mat @ value).to_euler()
		return _ret
	
	else:
		return convert_rotation_euler_to_blender

def _create_scale_to_blender_func(blender_object: bpy.types.Object) -> Callable:
	offset = mathutils.Vector([1, 1, 1])
	if(blender_object.parent_type == "OBJECT" and blender_object.parent):
		_, _, offset = (blender_object.parent.matrix_world).decompose()

	elif(blender_object.parent_type == "BONE" and blender_object.parent and blender_object.parent_bone):
		_, _, offset = (blender_object.parent.matrix_world).decompose()

	def _ret(value: list[float]) -> float:
		value = [value[i] * offset[i] for i in range(3)]
		return convert_scale_to_stf(value)
	return _ret


def stf_node_resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], blender_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "t":
			# todo handle parenting everywhere
			return blender_object, 0, "OBJECT", "location", translation_index_conversion_to_blender, _create_translation_to_blender_func(blender_object)
		case "r":
			return blender_object, 0, "OBJECT", "rotation_quaternion", rotation_index_conversion_to_blender, _create_rotation_to_blender_func(blender_object)
		case "r_euler":
			return blender_object, 0, "OBJECT", "rotation_euler", rotation_euler_index_conversion_to_blender, _create_rotation_euler_to_blender_func(blender_object)
		case "s":
			return blender_object, 0, "OBJECT", "scale", scale_index_conversion_to_blender, _create_scale_to_blender_func(blender_object)
		case "instance":
			module_ret =  context.resolve_stf_property_path([blender_object.stf_instance.stf_id] + stf_path[2:], blender_object)
			if(module_ret):
				target_object, application_object_property_index, slot_type, fcurve_target, index_table, conversion_func = module_ret # Ignore Target Object for now
				return blender_object, application_object_property_index, slot_type, fcurve_target, index_table, conversion_func
		case "components":
			module_ret =  context.resolve_stf_property_path(stf_path[2:], blender_object)
			if(module_ret):
				target_object, application_object_property_index, slot_type, fcurve_target, index_table, conversion_func = module_ret # Ignore Target Object for now
				return blender_object, application_object_property_index, slot_type, fcurve_target, index_table, conversion_func
		case "enabled":
			return blender_object, 0, "OBJECT", "hide_render", None, lambda v: [not v[0]]

	return None
