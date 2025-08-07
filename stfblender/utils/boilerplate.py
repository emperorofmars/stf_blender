import bpy

from .component_utils import STF_Component_Ref


def boilerplate_register(blender_type: any, stf_kind: str):
	blender_type.stf_id = bpy.props.StringProperty(name="ID", description="Universally unique ID") # type: ignore
	blender_type.stf_name = bpy.props.StringProperty(name="STF Name", description="Optional Name for STF export") # type: ignore
	blender_type.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth", description="Use Blender name or specify one manually") # type: ignore
	if(stf_kind not in ["instance", "comopnent"]):
		blender_type.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
		blender_type.stf_active_component_index = bpy.props.IntProperty(name="Selected Component")

def boilerplate_unregister(blender_type: any, stf_kind: str):
	if hasattr(blender_type, "stf_id"):
		del blender_type.stf_id
	if hasattr(blender_type, "stf_name"):
		del blender_type.stf_name
	if hasattr(blender_type, "stf_name_source_of_truth"):
		del blender_type.stf_name_source_of_truth
	if(stf_kind not in ["instance", "comopnent"]):
		if hasattr(blender_type, "stf_components"):
			del blender_type.stf_components
		if hasattr(blender_type, "stf_active_component_index"):
			del blender_type.stf_active_component_index
