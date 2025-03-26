import bpy
import re
from typing import Callable

from ...utils.animation_conversion_utils import get_rotation_to_stf_translation_func, get_scale_to_stf_translation_func, get_translation_to_stf_translation_func, translate_rotation_property_to_stf, translate_scale_property_to_stf, translate_translation_property_to_stf


def stf_node_translate_property_to_stf_func(blender_object: bpy.types.Object, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:

	if(match := re.search(r"^location", data_path)):
		return [blender_object.stf_id, "t", translate_translation_property_to_stf(data_index)], get_translation_to_stf_translation_func(data_index)

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [blender_object.stf_id, "r", translate_rotation_property_to_stf(data_index)], get_rotation_to_stf_translation_func(data_index)

	if(match := re.search(r"^scale", data_path)):
		return [blender_object.stf_id, "s", translate_scale_property_to_stf(data_index)], get_scale_to_stf_translation_func(data_index)

	# TODO object visibility

	return None


def stf_node_translate_property_to_blender_func(blender_object: bpy.types.Object, stf_property: str) -> tuple[str, int, Callable[[any], any]]:
	return stf_property, 0, None

