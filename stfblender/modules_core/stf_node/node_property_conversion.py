import bpy
import re
from typing import Callable

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ...utils.animation_conversion_utils import *


def stf_node_resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	if(match := re.search(r"^location", data_path)):
		return [application_object.stf_id, "t", translate_translation_property_to_stf(data_index)], get_translation_to_stf_translation_func(data_index)

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [application_object.stf_id, "r", translate_rotation_property_to_stf(data_index)], get_rotation_to_stf_translation_func(data_index)

	if(match := re.search(r"^scale", data_path)):
		return [application_object.stf_id, "s", translate_scale_property_to_stf(data_index)], get_scale_to_stf_translation_func(data_index)

	# TODO object visibility

	return None


def stf_node_resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, int, Callable[[any], any]]:
	blender_object = context.get_imported_resource(stf_path[0])
	match(stf_path[1]):
		case "t":
			data_index = translate_translation_property_to_blender(stf_path[2])
			return blender_object, 0, "OBJECT", "location", data_index, get_translation_to_blender_translation_func(data_index)
		case "r":
			data_index = translate_rotation_property_to_blender(stf_path[2])
			return blender_object, 0, "OBJECT", "rotation_quaternion", data_index, get_rotation_to_blender_translation_func(data_index)
		case "s":
			data_index = translate_scale_property_to_blender(stf_path[2])
			return blender_object, 0, "OBJECT", "scale", data_index, get_scale_to_blender_translation_func(data_index)
		case "instance" | "components":
			module_ret =  context.resolve_stf_property_path(stf_path[2:], blender_object)
			if(module_ret):
				target_object, application_object_property_index, slot_type, fcurve_target, property_index, conversion_func = module_ret # Ignore Target Object for now
				return blender_object, application_object_property_index, slot_type, fcurve_target, property_index, conversion_func

	# TODO object visibility

	return None
