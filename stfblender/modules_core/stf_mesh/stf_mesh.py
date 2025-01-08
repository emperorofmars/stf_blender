from io import BytesIO
import struct
import bpy
import bmesh

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STF_Report_Severity, STFReport
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_translation_to_stf


_stf_type = "stf.mesh"


def _stf_import(context: STF_RootImportContext, json: dict, id: str, parent_application_object: any) -> any:
	pass


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(blender_mesh)

	stf_mesh = {
		"type": _stf_type,
		"name": blender_mesh.name
	}

	bm = bmesh.new()
	bm.from_mesh(blender_mesh)

	buffer_vertices = BytesIO()
	for v in bm.verts:
		position = blender_translation_to_stf(v.co)
		buffer_vertices.write(struct.pack("<f", position.x))
		buffer_vertices.write(struct.pack("<f", position.y))
		buffer_vertices.write(struct.pack("<f", position.z))

	buffer_virtual_vertices = BytesIO()
	buffer_normals = BytesIO()
	buffer_tangents = BytesIO()
	buffer_colors = BytesIO()

	buffer_lines = BytesIO()

	buffer_tris = BytesIO()
	buffer_faces = BytesIO()

	# for each weight channel
	buffer_weights_indices = BytesIO()
	buffer_weights_target = BytesIO()
	buffer_weights = BytesIO()

	# for each blendshape
	buffer_blendshape_indices = BytesIO()
	buffer_blendshape_translation = BytesIO()
	buffer_blendshape_normal = BytesIO()
	buffer_blendshape_tangent = BytesIO()


	stf_mesh["mesh"] = context.serialize_buffer(buffer_vertices)

	return stf_mesh, blender_mesh.stf_id, context


class STF_Module_STF_Mesh(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["mesh"]
	understood_application_types = [bpy.types.Mesh]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Mesh
]


def register():
	bpy.types.Mesh.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Mesh.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Mesh.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Mesh, "stf_id"):
		del bpy.types.Mesh.stf_id
	if hasattr(bpy.types.Mesh, "stf_components"):
		del bpy.types.Mesh.stf_components
	if hasattr(bpy.types.Mesh, "stf_active_component_index"):
		del bpy.types.Mesh.stf_active_component_index

