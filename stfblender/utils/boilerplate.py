import bpy

from ..base.stf_info import STF_Info


def boilerplate_register(blender_type: any, stf_kind: str):
	blender_type.stf_info = bpy.props.PointerProperty(type=STF_Info, name="STF Info")

def boilerplate_unregister(blender_type: any, stf_kind: str):
	if hasattr(blender_type, "stf_info"):
		del blender_type.stf_info
