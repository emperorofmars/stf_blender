import bpy

from ....common import STF_Category
from ....common.resource import STF_Handler_BlenderNative, STF_HandlerComponents, boilerplate_register, boilerplate_unregister, get_components_from_object
from ....common.helpers import draw_multiline_text
from .mesh_import import import_stf_mesh
from .mesh_export import export_stf_mesh
from .stf_mesh_ui import STFAddMeshComponentOperator, STFEditMeshComponentIdOperator, STFRemoveMeshComponentOperator, STFSetMeshIDOperator


_stf_type = "stf.mesh"


class STF_Mesh(bpy.types.PropertyGroup):
	export_blendshape_normals: bpy.props.BoolProperty(name="Export Shapekey Normals", default=True, options=set())
	export_vertex_colors: bpy.props.BoolProperty(name="Export Vertex Colors", default=True, options=set())


def draw_mesh_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: bpy.types.Mesh) -> None:
	if(context.object.find_armature()):
		t, r, s = context.object.matrix_local.decompose()
		if(t.length > 0.0001 or abs(r.x) > 0.0001 or abs(r.y) > 0.0001 or abs(r.z) > 0.0001 or abs((r.w - 1)) > 0.0001 or abs(s.x - 1) > 0.0001 or abs(s.y - 1) > 0.0001 or abs(s.z - 1) > 0.0001):
			draw_multiline_text(layout, "Warning, this mesh is not aligned with its Armature!\nThis will lead to differing behavior outside of Blender.\nApplying all Transforms for the Mesh and Armature will likely fix this.", width=80, icon="ERROR", alert=True)
			layout.separator(factor=2, type="LINE")

	layout.prop(context.mesh.stf_mesh, "export_blendshape_normals")
	layout.prop(context.mesh.stf_mesh, "export_vertex_colors")


class Handler_STF_Mesh(STF_Handler_BlenderNative, STF_HandlerComponents):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["mesh"]
	understood_application_types = [bpy.types.Mesh]
	import_func = import_stf_mesh
	export_func = export_stf_mesh
	operator_set_stf_id = STFSetMeshIDOperator.bl_idname
	draw = draw_mesh_ui

	get_components_func = get_components_from_object
	operator_component_add = STFAddMeshComponentOperator.bl_idname
	operator_component_remove = STFRemoveMeshComponentOperator.bl_idname
	operator_component_edit = STFEditMeshComponentIdOperator.bl_idname


register_stf_handlers = [
	Handler_STF_Mesh
]


def register():
	bpy.types.Mesh.stf_mesh = bpy.props.PointerProperty(type=STF_Mesh)
	boilerplate_register(bpy.types.Mesh)

def unregister():
	boilerplate_unregister(bpy.types.Mesh)
	if hasattr(bpy.types.Mesh, "stf_mesh"):
		del bpy.types.Mesh.stf_mesh
