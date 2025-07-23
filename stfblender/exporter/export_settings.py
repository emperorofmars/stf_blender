import bpy


class STF_ExportSettings(bpy.types.PropertyGroup):
	stf_mesh_vertex_colors: bpy.props.BoolProperty(name="Vertex Colors", default=True) # type: ignore
	stf_mesh_blendshape_normals: bpy.props.BoolProperty(name="Blendshape Normals", default=True) # type: ignore

