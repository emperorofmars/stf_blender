import bpy
import re
from typing import Callable

from ....libstf.stf_export_context import STF_ExportContext
from ...utils.animation_conversion_utils import *


def stf_node_resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	if(match := re.search(r"^location", data_path)):
		return [application_object.stf_id, "t", translate_translation_property_to_stf(data_index)], get_translation_to_stf_translation_func(data_index)

	if(match := re.search(r"^rotation_quaternion", data_path)):
		return [application_object.stf_id, "r", translate_rotation_property_to_stf(data_index)], get_rotation_to_stf_translation_func(data_index)

	if(match := re.search(r"^scale", data_path)):
		return [application_object.stf_id, "s", translate_scale_property_to_stf(data_index)], get_scale_to_stf_translation_func(data_index)

	# TODO object visibility

	return None

