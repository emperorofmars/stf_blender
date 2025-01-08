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

	print("Exporting: " + str(blender_mesh))

	bm = bmesh.new()
	bm.from_mesh(blender_mesh)
	bm.verts.index_update()
	bm.edges.index_update()
	bm.faces.index_update()

	bm_tris: list[tuple[bmesh.types.BMLoop, bmesh.types.BMLoop, bmesh.types.BMLoop]] = bm.calc_loop_triangles()

	vertex_indices_width = 4 if len(bm.verts) * 3 < 2**31 else 8
	split_indices_width = 4 if len(bm_tris) * 3 < 2**31 else 8
	float_width = 4

	stf_mesh = {
		"type": _stf_type,
		"name": blender_mesh.name,
		"vertex_count": len(bm.verts),
		"vertex_indices_width": vertex_indices_width,
		"split_count": len(bm_tris) * 3,
		"split_indices_width": split_indices_width,
		"vertex_pos_width": float_width,
	}

	buffer_vertices = BytesIO()
	buffer_colors = BytesIO()

	for vertex in bm.verts:
		position = blender_translation_to_stf(vertex.co)
		buffer_vertices.write(struct.pack("<f", position[0]))
		buffer_vertices.write(struct.pack("<f", position[1]))
		buffer_vertices.write(struct.pack("<f", position[2]))

	buffer_split_vertices = BytesIO()
	buffer_normals = BytesIO()
	buffer_tangents = BytesIO()

	buffer_lines = BytesIO()

	buffer_tris = BytesIO()
	buffer_faces = BytesIO()

	for face in bm.faces:
		for loop in face.loops:
			buffer_split_vertices.write(loop.vert.index.to_bytes(length=vertex_indices_width, byteorder="little"))

			normal = blender_translation_to_stf(loop.calc_normal())
			buffer_normals.write(struct.pack("<f", normal[0]))
			buffer_normals.write(struct.pack("<f", normal[1]))
			buffer_normals.write(struct.pack("<f", normal[2]))

			tangent = blender_translation_to_stf(loop.calc_tangent())
			buffer_tangents.write(struct.pack("<f", tangent[0]))
			buffer_tangents.write(struct.pack("<f", tangent[1]))
			buffer_tangents.write(struct.pack("<f", tangent[2]))

	face_lens: list[int] = [0]
	last_face_index = 0
	for tri in bm_tris:
		if(last_face_index == tri[0].face.index):
			face_lens[len(face_lens) - 1] += 1
		else:
			face_lens.append(1)

		buffer_tris.write(tri[0].index.to_bytes(length=split_indices_width, byteorder="little"))
		buffer_tris.write(tri[1].index.to_bytes(length=split_indices_width, byteorder="little"))
		buffer_tris.write(tri[2].index.to_bytes(length=split_indices_width, byteorder="little"))

		last_face_index = tri[0].face.index

	for face_len in face_lens:
		buffer_faces.write(face_len.to_bytes(length=4, byteorder="little"))

	# for each weight channel and vertex
	buffer_weights_indices = BytesIO()
	buffer_weights_target = BytesIO()
	buffer_weights = BytesIO()

	# for each blendshape and vertex
	buffer_blendshape_indices = BytesIO()
	buffer_blendshape_translation = BytesIO()
	buffer_blendshape_normal = BytesIO()
	buffer_blendshape_tangent = BytesIO()


	stf_mesh["vertices"] = context.serialize_buffer(buffer_vertices)
	stf_mesh["splits"] = context.serialize_buffer(buffer_split_vertices)
	stf_mesh["normals"] = context.serialize_buffer(buffer_normals)
	stf_mesh["tangents"] = context.serialize_buffer(buffer_tangents)
	stf_mesh["tris"] = context.serialize_buffer(buffer_tris)
	stf_mesh["faces"] = context.serialize_buffer(buffer_faces)

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

