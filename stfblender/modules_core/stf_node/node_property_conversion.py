import bpy
import re
from typing import Callable

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ...utils.animation_conversion_utils import *


def stf_node_resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^location", data_path)):
		return [application_object.stf_id, "t"], convert_translation_to_stf, translation_index_conversion_to_stf

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [application_object.stf_id, "r"], convert_blender_rotation_to_stf, rotation_index_conversion_to_stf

	if(match := re.search(r"^scale", data_path)):
		return [application_object.stf_id, "s"], convert_scale_to_stf, scale_index_conversion_to_stf

	# TODO object visibility

	return None


def stf_node_resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[int, any], any]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "t":
			return blender_object, 0, "OBJECT", "location", translation_index_conversion_to_blender, convert_translation_to_blender
		case "r":
			return blender_object, 0, "OBJECT", "rotation_quaternion", rotation_index_conversion_to_blender, convert_rotation_to_blender
		case "s":
			return blender_object, 0, "OBJECT", "scale", scale_index_conversion_to_blender, convert_scale_to_blender
		case "instance" | "components":
			module_ret =  context.resolve_stf_property_path(stf_path[2:], blender_object)
			if(module_ret):
				target_object, application_object_property_index, slot_type, fcurve_target, index_table, conversion_func = module_ret # Ignore Target Object for now
				return blender_object, application_object_property_index, slot_type, fcurve_target, index_table, conversion_func

	# TODO object visibility

	return None
