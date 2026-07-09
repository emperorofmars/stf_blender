import bpy

"""
STF data-resources that aren't natively supported by Blender, similar to components, are stored by the Collection that represents the STF-Prefab.
"""

from .stf_resource_component import STF_Component_Ref

class STF_Data_Ref(bpy.types.PropertyGroup):
	stf_type: bpy.props.StringProperty(name="Type", options=set()) # type: ignore
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name", options=set()) # type: ignore


class STF_DataResourceBase(bpy.types.PropertyGroup):
	"""Base class for stf data-resources which are non-native to Blender"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="Name", options=set()) # type: ignore
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components", options=set()) # type: ignore
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component", options=set()) # type: ignore


def register():
	# For STF-Data modules
	bpy.types.Collection.stf_data_refs = bpy.props.CollectionProperty(type=STF_Data_Ref, name="STF Data Refs", options=set())
	bpy.types.Collection.stf_data_ref_selected = bpy.props.IntProperty(options=set())

def unregister():
	# For STF-Data modules
	if hasattr(bpy.types.Collection, "stf_data_ref_selected"):
		del bpy.types.Collection.stf_data_ref_selected
	if hasattr(bpy.types.Collection, "stf_data_refs"):
		del bpy.types.Collection.stf_data_refs
