import bpy

from ....base.stf_module import STF_Module
from ....utils.component_utils import get_components_from_object
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister

from .mesh_import import import_stf_mesh
from .mesh_export import export_stf_mesh


_stf_type = "stf.mesh"


class STF_Mesh(bpy.types.PropertyGroup):
	export_blendshape_normals: bpy.props.BoolProperty(name="Export Shapekey Normals", default=True, options=set()) # type: ignore
	export_vertex_colors: bpy.props.BoolProperty(name="Export Vertex Colors", default=True, options=set()) # type: ignore


class STF_Module_STF_Mesh(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["mesh"]
	understood_application_types = [bpy.types.Mesh]
	import_func = import_stf_mesh
	export_func = export_stf_mesh
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Mesh
]


def register():
	bpy.types.Mesh.stf_mesh = bpy.props.PointerProperty(type=STF_Mesh)
	boilerplate_register(bpy.types.Mesh, "data")

def unregister():
	boilerplate_unregister(bpy.types.Mesh, "data")
	if hasattr(bpy.types.Mesh, "stf_mesh"):
		del bpy.types.Mesh.stf_mesh
