import bpy
from typing import Any

from ..stf_info import STF_Info


def boilerplate_register(blender_type: Any, stf_kind: str):
	blender_type.stf_info = bpy.props.PointerProperty(type=STF_Info, name="STF Info", options=set())

def boilerplate_unregister(blender_type: Any, stf_kind: str):
	if hasattr(blender_type, "stf_info"):
		del blender_type.stf_info
