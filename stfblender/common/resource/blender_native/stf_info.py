import bpy
from typing import Any

from ..component.stf_handler_component import STF_Component_Ref

__all__ = ["STF_Info", "boilerplate_register", "boilerplate_unregister", "get_components_from_object"]

class STF_Info(bpy.types.PropertyGroup):
	"""Basic STF properties for Blender structs that represent stf-node or stf-data resources"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional Name for STF export", options=set()) # type: ignore
	stf_name_source_of_truth: bpy.props.BoolProperty(name="STF Name Is Source Of Truth", description="Use Blender name or specify one manually", options=set()) # type: ignore
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components", options=set()) # type: ignore
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component", options=set()) # type: ignore


def boilerplate_register(blender_type: Any):
	blender_type.stf_info = bpy.props.PointerProperty(type=STF_Info, name="STF Info", options=set())

def boilerplate_unregister(blender_type: Any):
	if hasattr(blender_type, "stf_info"):
		del blender_type.stf_info


def get_components_from_object(blender_object: Any) -> list[Any]:
	"""Retrieves Blender STF components from an Blender object"""
	ret = []
	if(hasattr(blender_object, "stf_info")):
		for component_ref in blender_object.stf_info.stf_components:
			if(hasattr(blender_object, component_ref.blender_property_name)):
				components = getattr(blender_object, component_ref.blender_property_name)
				for component in components:
					if(component.stf_id == component_ref.stf_id):
						ret.append(component)
	return ret
