import bpy
from typing import Callable

from ..base.stf_module_component import STF_BlenderComponentBase

"""
Export
"""

# Translation
translation_index_conversion_to_stf = [0, 2, 1]
def convert_translation_to_stf(index: int, value: float) -> float:
	match(index):
		case 0: return value
		case 1: return value
		case 2: return -value
	return None

translation_bone_index_conversion_to_stf = [0, 1, 2]
def convert_bone_translation_to_stf(index: int, value: float) -> float:
	return value

# Rotation
rotation_index_conversion_to_stf = [3, 0, 2, 1]
def convert_blender_rotation_to_stf(index: int, value: float) -> float:
	match(index):
		case 0: return value
		case 1: return value
		case 2: return -value
		case 3: return value
	return None

rotation_bone_index_conversion_to_stf = [3, 0, 1, 2]
def convert_bone_rotation_to_stf(index: int, value: float) -> float:
	return value

# Scale
scale_index_conversion_to_stf = [0, 2, 1]
def convert_scale_to_stf(index: int, value: float) -> float:
	return value

scale_bone_index_conversion_to_stf = [0, 1, 2]
def convert_bone_scale_to_stf(index: int, value: float) -> float:
	return value


# components
def get_component_stf_path(application_object: any, component: STF_BlenderComponentBase):
	for component_ref in application_object.stf_info.stf_components:
		if(component_ref.stf_id == component.stf_id):
			return [application_object.stf_info.stf_id, "components", component.stf_id]
	if(type(application_object.data) == bpy.types.Armature):
		for component_ref in application_object.stf_instance_armature.stf_components:
			if(component_ref.stf_id == component.stf_id):
				return [application_object.stf_info.stf_id, "instance", application_object.data.bones[component_ref.bone].stf_info.stf_id, "components", component.stf_id]
		for component_ref in application_object.stf_instance_armature_component_standins.stf_components:
			if(component_ref.stf_id == component.stf_id):
				return [application_object.stf_info.stf_id, "instance", application_object.data.bones[component_ref.bone].stf_info.stf_id, "component_mods", component.stf_id]
	return None


"""
Import
"""

# Translation
translation_index_conversion_to_blender = [0, 2, 1]
def convert_translation_to_blender(index: int, value: float) -> float:
	match(index):
		case 0: return value
		case 1: return value
		case 2: return -value
	return None

translation_bone_index_conversion_to_blender = [0, 1, 2]
def convert_bone_translation_to_blender(index: int, value: float) -> float:
	return value

# Rotation
rotation_index_conversion_to_blender = [1, 3, 2, 0]
def convert_rotation_to_blender(index: int, value: float) -> Callable[[any], any]:
	match(index):
		case 0: return value
		case 1: return value
		case 2: return -value
		case 3: return value
	return None

rotation_index_bone_conversion_to_blender = [1, 2, 3, 0]
def convert_bone_rotation_to_blender(index: int, value: float) -> Callable[[any], any]:
	return value

# Scale
scale_index_conversion_to_blender = [0, 2, 1]
def convert_scale_to_blender(index: int, value: float) -> float:
	return value

scale_bone_index_conversion_to_blender = [0, 1, 2]
def convert_bone_scale_to_blender(index: int, value: float) -> float:
	return value
