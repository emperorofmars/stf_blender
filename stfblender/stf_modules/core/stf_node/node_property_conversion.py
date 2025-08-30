import re
import mathutils
from typing import Callable

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.animation_conversion_utils import *


def _convert_relative_translation_to_stf(application_object: bpy.types.Object) -> Callable:
	parent_location = mathutils.Vector()
	# todo make this more proper, deal with parent_matrix_inverse and shit
	if(application_object.parent_type == "OBJECT" and application_object.parent):
		parent_location = application_object.parent.matrix_world.translation - (application_object.matrix_world.translation - application_object.location)
	elif(application_object.parent_type == "BONE" and application_object.parent and application_object.parent_bone):
		# The animated value is the 'location'. Unfortunately, there is a very good chance it is completely bullshit, with (0, 0, 0) being a completely random point, not at the world origin or the parent.
		# This is due to the 'parent_matrix_inverse'. It should be a computed value, as should be the 'location'. The animated property here should be consistent in relation to something, be it the world origin or parent.
		# ffs Blender
		bone: bpy.types.PoseBone = application_object.parent.pose.bones[application_object.parent_bone]
		head_location = (application_object.parent.matrix_world @ mathutils.Matrix.Translation(bone.tail - bone.head) @ bone.matrix).translation
		parent_location = head_location - (application_object.matrix_world.translation - application_object.location)

	def _ret(value: list[float]) -> float:
		value = [value[i] - parent_location[i] for i in range(len(value))]
		return convert_translation_to_stf(value)
	return _ret

def stf_node_resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: bpy.types.Object, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[list[float]], list[float]], list[int]]:
	if(match := re.search(r"^location", data_path)):
		# todo handle bone parents
		return [application_object.stf_info.stf_id, "t"], _convert_relative_translation_to_stf(application_object), translation_index_conversion_to_stf

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [application_object.stf_info.stf_id, "r"], convert_blender_rotation_to_stf, rotation_index_conversion_to_stf

	if(match := re.search(r"^rotation_euler", data_path)):
		return [application_object.stf_info.stf_id, "r_euler"], convert_rotation_euler_to_stf, rotation_euler_index_conversion_to_stf

	if(match := re.search(r"^scale", data_path)):
		return [application_object.stf_info.stf_id, "s"], convert_scale_to_stf, scale_index_conversion_to_stf

	if(match := re.search(r"^hide_render", data_path)):
		return [application_object.stf_info.stf_id, "enabled"], lambda v: [not v[0]], None

	return None


def _convert_relative_translation_to_blender(application_object: bpy.types.Object) -> Callable:
	parent_location = mathutils.Vector()
	if(application_object.parent_type == "OBJECT" and application_object.parent):
		parent_location = application_object.parent.location
	elif(application_object.parent_type == "BONE" and application_object.parent and application_object.parent_bone):
		parent_location = application_object.matrix_parent_inverse.inverted_safe().translation # This is only correct at time of import. Afterward there is no guarantee of this being useful.

	def _ret(value: list[float]) -> list[float]:
		value = convert_translation_to_blender(value)[:]
		value = [value[i] + parent_location[i] for i in range(len(value))]
		return value
	return _ret

def stf_node_resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "t":
			# todo handle bone parents
			return blender_object, 0, "OBJECT", "location", translation_index_conversion_to_blender, _convert_relative_translation_to_blender(blender_object)
		case "r":
			return blender_object, 0, "OBJECT", "rotation_quaternion", rotation_index_conversion_to_blender, convert_rotation_to_blender
		case "r_euler":
			return blender_object, 0, "OBJECT", "rotation_euler", rotation_euler_index_conversion_to_blender, convert_rotation_euler_to_blender
		case "s":
			return blender_object, 0, "OBJECT", "scale", scale_index_conversion_to_blender, convert_scale_to_blender
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
