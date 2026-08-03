import bpy


class STF_Instance_Mesh_Blendshape_Value(bpy.types.PropertyGroup):
	value: bpy.props.FloatProperty(name="Value", default=0, soft_min=0, soft_max=1, precision=3, subtype="FACTOR", description="Instance specific value for this shape key. To animate this, please animate the Meshes actual shape keys and set this Object as the target with the SlotLink extension.", options=set())

class STF_Instance_Mesh(bpy.types.PropertyGroup):
	blendshape_values: bpy.props.CollectionProperty(type=STF_Instance_Mesh_Blendshape_Value, name="Shape Key Values", options=set())
	active_blendshape: bpy.props.IntProperty(options=set())

