import bpy

from .stf_module_component import STF_Component_Ref


class STF_Info(bpy.types.PropertyGroup):
	"""Basic STF properties"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional Name for STF export", options=set()) # type: ignore
	stf_name_source_of_truth: bpy.props.BoolProperty(name="STF Name Is Source Of Truth", description="Use Blender name or specify one manually", options=set()) # type: ignore
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components", options=set()) # type: ignore
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component", options=set()) # type: ignore
