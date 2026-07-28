from typing import Any

import bpy

from .....stfblender_common import STF_Category, STF_ImportContext, STF_ExportContext, STFReport, STF_Handler_BlenderNative, STF_Handler_ComponentHolder, boilerplate_register, boilerplate_unregister, get_components_from_object
from .....stfblender_common.helpers import draw_multiline_text
from .mesh_import import import_stf_mesh
from .mesh_export import export_stf_mesh
from .stf_mesh_ops import STFAddMeshComponentOperator, STFEditMeshComponentIdOperator, STFRemoveMeshComponentOperator, STFSetMeshIDOperator
from .mesh_common import stf_mesh_type


class STF_Mesh(bpy.types.PropertyGroup):
	export_blendshape_normals: bpy.props.BoolProperty(name="Export Shapekey Normals", default=True, options=set())
	export_vertex_colors: bpy.props.BoolProperty(name="Export Vertex Colors", default=True, options=set())


class Handler_STF_Mesh(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = stf_mesh_type
	stf_category = STF_Category.DATA
	like_types = ["mesh"]
	understood_blender_types = [bpy.types.Mesh]
	operator_set_stf_id = STFSetMeshIDOperator.bl_idname

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: bpy.types.Mesh) -> None:
		if(context.object.find_armature()):
			t, r, s = context.object.matrix_local.decompose()
			if(t.length > 0.0001 or abs(r.x) > 0.0001 or abs(r.y) > 0.0001 or abs(r.z) > 0.0001 or abs((r.w - 1)) > 0.0001 or abs(s.x - 1) > 0.0001 or abs(s.y - 1) > 0.0001 or abs(s.z - 1) > 0.0001):
				draw_multiline_text(layout, "Warning, this mesh is not aligned with its Armature!\nThis will lead to differing behavior outside of Blender.\nApplying all Transforms for the Mesh and Armature will likely fix this.", width=80, icon="ERROR", alert=True)
				layout.separator(factor=2, type="LINE")

		layout.prop(context.mesh.stf_mesh, "export_blendshape_normals")
		layout.prop(context.mesh.stf_mesh, "export_vertex_colors")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		return import_stf_mesh(context, json_resource, stf_id, context_resource)

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str] | STFReport:
		return export_stf_mesh(context, blender_resource, context_resource)

	get_components = get_components_from_object
	operator_component_add = STFAddMeshComponentOperator.bl_idname
	operator_component_remove = STFRemoveMeshComponentOperator.bl_idname
	operator_component_edit = STFEditMeshComponentIdOperator.bl_idname


def register():
	bpy.types.Mesh.stf_mesh = bpy.props.PointerProperty(type=STF_Mesh)
	boilerplate_register(bpy.types.Mesh)

def unregister():
	boilerplate_unregister(bpy.types.Mesh)
	if hasattr(bpy.types.Mesh, "stf_mesh"):
		del bpy.types.Mesh.stf_mesh
