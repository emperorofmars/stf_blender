import bpy

from ..lib_stfblender.module_data.stf_module_data import STF_Data_Ref


def register():
	# For STF-Data modules
	bpy.types.Collection.stf_data_refs = bpy.props.CollectionProperty(type=STF_Data_Ref, name="STF Data Refs", options=set()) # type: ignore
	bpy.types.Collection.stf_data_ref_selected = bpy.props.IntProperty(options=set()) # type: ignore

	# For STF ID Utils
	bpy.types.Scene.stf_edit_resource_id = bpy.props.BoolProperty(name="Edit ID", description="Toggle the editing of the ID", default=False)

def unregister():
	# For STF ID Utils
	if hasattr(bpy.types.Scene, "stf_edit_resource_id"):
		del bpy.types.Scene.stf_edit_resource_id

	# For STF-Data modules
	if hasattr(bpy.types.Collection, "stf_data_ref_selected"):
		del bpy.types.Collection.stf_data_ref_selected
	if hasattr(bpy.types.Collection, "stf_data_refs"):
		del bpy.types.Collection.stf_data_refs

