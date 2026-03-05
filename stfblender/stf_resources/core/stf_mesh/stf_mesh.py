import bpy

from ....common import STF_Category
from ....common.resource.blender_native import STF_Handler_BlenderNative
from ....common.resource.component.component_utils import get_components_from_object
from ....common.utils.boilerplate import boilerplate_register, boilerplate_unregister
from .mesh_import import import_stf_mesh
from .mesh_export import export_stf_mesh


_stf_type = "stf.mesh"


class STF_Mesh(bpy.types.PropertyGroup):
	export_blendshape_normals: bpy.props.BoolProperty(name="Export Shapekey Normals", default=True, options=set()) # type: ignore
	export_vertex_colors: bpy.props.BoolProperty(name="Export Vertex Colors", default=True, options=set()) # type: ignore


class Handler_STF_Mesh(STF_Handler_BlenderNative):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["mesh"]
	understood_application_types = [bpy.types.Mesh]
	import_func = import_stf_mesh
	export_func = export_stf_mesh
	get_components_func = get_components_from_object


register_stf_handlers = [
	Handler_STF_Mesh
]


def register():
	bpy.types.Mesh.stf_mesh = bpy.props.PointerProperty(type=STF_Mesh)
	boilerplate_register(bpy.types.Mesh, STF_Category.DATA)

def unregister():
	boilerplate_unregister(bpy.types.Mesh, STF_Category.DATA)
	if hasattr(bpy.types.Mesh, "stf_mesh"):
		del bpy.types.Mesh.stf_mesh
