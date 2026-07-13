import bpy
from typing import Any, Protocol
from collections.abc import Callable

from .stf_info import STF_Info
from ..stf_handler_base import STF_HandlerBase


__all__ = ["STF_Handler_BlenderNative"]


class STF_Handler_BlenderNative(STF_HandlerBase, Protocol):
	"""Represents functionality to import and export a Blender-native resource"""

	get_resource_object: Callable[[Any], Any] = lambda bo: bo
	"""
	`lambda bo: bo`

	Get the actual Blender representation of a resource.
	This is mostly a workaround for having to wrap Bone references inside an `ArmatureBone` object.

	:param Any blender_object:
	:return bpy_struct: The Blender object that actually represents the resource
	"""

	get_stf_prop_holder: Callable[[Any], STF_Info] = lambda bo: bo.stf_info
	"""
	`get_stf_prop_holder = lambda bo: bo.stf_info`

	Get the property from a Blender object that holds the `stf_id` property.

	:param Any blender_object:
	:return bpy_struct: The Blender object that has the `stf_id` property.
	"""

	draw: Callable[[bpy.types.UILayout, bpy.types.Context, Any], None | bool]
	"""
	`def draw(layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: Any) -> None`

	Draw the GUI for the stf resource.

	:param bpy.types.UILayout layout:
	:param bpy.types.Context context:
	:param Any blender_resource: The Blender representation of the STF resource.
	:return None | bool: Return `False` if no GUI has been added to the layout, otherwise `None`.
	"""

	operator_set_stf_id: str
	"""
	`bl_idname` of the operator that can set the stf_id for this resource.
	"""
