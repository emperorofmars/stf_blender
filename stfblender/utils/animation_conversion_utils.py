import bpy
from typing import Callable

from ..base.stf_module_component import STF_BlenderComponentBase
from ..utils import trs_utils


"""
Export
"""

# Translation
translation_index_conversion_to_stf = [0, 2, 1]
convert_translation_to_stf = trs_utils.blender_translation_to_stf

translation_bone_index_conversion_to_stf = [0, 1, 2]
def convert_bone_translation_to_stf(value: list[float]): return value


# Rotation
rotation_index_conversion_to_stf = [1, 3, 2, 0]
convert_blender_rotation_to_stf = trs_utils.blender_rotation_to_stf

rotation_bone_index_conversion_to_stf = [1, 2, 3, 0]
def convert_bone_rotation_to_stf(value: list[float]):
	return [value[1], value[2], value[3], value[0]]

# Rotation Euler
rotation_euler_index_conversion_to_stf = [0, 2, 1]
convert_rotation_euler_to_stf = trs_utils.blender_rotation_euler_to_stf

rotation_euler_bone_index_conversion_to_stf = [0, 1, 2]
def convert_bone_rotation_euler_to_stf(value: list[float]): return value


# Scale
scale_index_conversion_to_stf = [0, 2, 1]
convert_scale_to_stf = trs_utils.blender_scale_to_stf

scale_bone_index_conversion_to_stf = [0, 1, 2]
def convert_bone_scale_to_stf(value: list[float]): return value


# Components
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
convert_translation_to_blender = trs_utils.stf_translation_to_blender

translation_bone_index_conversion_to_blender = [0, 1, 2]
def convert_bone_translation_to_blender(value: list[float]): return value

# Rotation
rotation_index_conversion_to_blender = [3, 0, 2, 1]
convert_rotation_to_blender = trs_utils.stf_rotation_to_blender


rotation_index_bone_conversion_to_blender = [3, 0, 1, 2]
def convert_bone_rotation_to_blender(value: list[float]): return value


# Rotation Euler
rotation_euler_index_conversion_to_blender = [0, 2, 1]
convert_rotation_euler_to_blender = trs_utils.stf_rotation_euler_to_blender

rotation_euler_bone_index_conversion_to_blender = [0, 1, 2]
def convert_bone_rotation_euler_to_blender(value: list[float]): return value


# Scale
scale_index_conversion_to_blender = [0, 2, 1]
convert_scale_to_blender = trs_utils.stf_scale_to_blender

scale_bone_index_conversion_to_blender = [0, 1, 2]
def convert_bone_scale_to_blender(value: list[float]): return value
