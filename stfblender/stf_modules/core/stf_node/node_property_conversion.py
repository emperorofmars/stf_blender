import re
import mathutils
from typing import Callable

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.animation_conversion_utils import *


def _convert_relative_translation_to_stf(parent_location: mathutils.Vector) -> Callable:
	def _ret(index: int, value: float) -> float:
		return convert_translation_to_stf(index, value - parent_location[translation_index_conversion_to_blender[index]])
	return _ret


def stf_node_resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: bpy.types.Object, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^location", data_path)):
		return [application_object.stf_info.stf_id, "t"], _convert_relative_translation_to_stf(application_object.parent.location if application_object.parent else mathutils.Vector()), translation_index_conversion_to_stf

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [application_object.stf_info.stf_id, "r"], convert_blender_rotation_to_stf, rotation_index_conversion_to_stf

	if(match := re.search(r"^rotation_euler", data_path)):
		return [application_object.stf_info.stf_id, "r_euler"], convert_rotation_euler_to_stf, rotation_euler_index_conversion_to_stf

	if(match := re.search(r"^scale", data_path)):
		return [application_object.stf_info.stf_id, "s"], convert_scale_to_stf, scale_index_conversion_to_stf

	if(match := re.search(r"^hide_render", data_path)):
		return [application_object.stf_info.stf_id, "enabled"], lambda i, v: not v, None

	return None


def stf_node_resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: bpy.types.Object) -> tuple[any, int, any, any, list[int], Callable[[int, any], any]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "t":
			return blender_object, 0, "OBJECT", "location", translation_index_conversion_to_blender, convert_translation_to_blender
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
			return blender_object, 0, "OBJECT", "hide_render", 0, lambda i, v: not v

	return None