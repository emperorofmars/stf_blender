import bpy

from ..lib_stfblender.module_data.stf_module_data import STF_Data_Ref


def register():
	bpy.types.Collection.stf_data_refs = bpy.props.CollectionProperty(type=STF_Data_Ref, name="STF Data Refs", options=set()) # type: ignore
	bpy.types.Collection.stf_data_ref_selected = bpy.props.IntProperty(options=set()) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_data_ref_selected"):
		del bpy.types.Collection.stf_data_ref_selected
	if hasattr(bpy.types.Collection, "stf_data_refs"):
		del bpy.types.Collection.stf_data_refs
