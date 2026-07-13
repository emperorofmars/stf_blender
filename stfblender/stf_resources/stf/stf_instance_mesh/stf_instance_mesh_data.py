import bpy


class STF_Instance_Mesh_Blendshape_Value(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Name", options=set()) # type: ignore
	override: bpy.props.BoolProperty(name="Override", default=False, options=set()) # type: ignore
	value: bpy.props.FloatProperty(name="Value", default=0, soft_min=0, soft_max=1, precision=3, subtype="FACTOR") # type: ignore
	index_on_mesh: bpy.props.IntProperty(name="Index") # type: ignore

class STF_Instance_Mesh(bpy.types.PropertyGroup):
	override_blendshape_values: bpy.props.BoolProperty(name="Override Blendshape Values", default=False, options=set()) # type: ignore
	blendshape_values: bpy.props.CollectionProperty(type=STF_Instance_Mesh_Blendshape_Value, name="Blendshape Values", options=set()) # type: ignore
	active_blendshape: bpy.props.IntProperty(options=set()) # type: ignore

