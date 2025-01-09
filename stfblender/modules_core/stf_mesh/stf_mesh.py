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


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> any:
	blender_mesh = bpy.data.meshes.new(json_resource.get("name", "STF Mesh"))
	blender_mesh.stf_id = id
	return blender_mesh


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(blender_mesh)

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
		"name": blender_mesh.stf_name if blender_mesh.stf_name else blender_mesh.name,
		"vertex_count": len(bm.verts),
		"vertex_indices_width": vertex_indices_width,
		"split_count": len(bm_tris) * 3,
		"split_indices_width": split_indices_width,
		"vertex_pos_width": float_width,
	}

	buffer_vertices = BytesIO()
	# The vertex only stores the position. Normals, uv's, etc... are stored by split vertices. The vertex is here to inform the application that these many split vertices are actually the same point.
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
	buffer_tris_material_index = BytesIO()
	buffer_faces = BytesIO()

	bm_color_layers = bm.loops.layers.color
	buffers_color: list[BytesIO] = []
	for _ in bm_color_layers:
		buffers_color.append(BytesIO())

	bm_uv_layers = bm.loops.layers.uv
	buffers_uv: list[BytesIO] = []
	for _ in bm_uv_layers:
		buffers_uv.append(BytesIO())

	for face in bm.faces:
		for loop in face.loops:
			# Splits vertices reference the 'real' vertex by index. The normal, tangent, uv, etc... indices correspond to the split vertices index.
			buffer_split_vertices.write(loop.vert.index.to_bytes(length=vertex_indices_width, byteorder="little"))

			normal = blender_translation_to_stf(loop.calc_normal())
			buffer_normals.write(struct.pack("<f", normal[0]))
			buffer_normals.write(struct.pack("<f", normal[1]))
			buffer_normals.write(struct.pack("<f", normal[2]))

			tangent = blender_translation_to_stf(loop.calc_tangent())
			buffer_tangents.write(struct.pack("<f", tangent[0]))
			buffer_tangents.write(struct.pack("<f", tangent[1]))
			buffer_tangents.write(struct.pack("<f", tangent[2]))

			for index, color_layer in enumerate(bm_color_layers):
				buffers_color[index].write(struct.pack("<f", loop[color_layer].color[0]))
				buffers_color[index].write(struct.pack("<f", loop[color_layer].color[1]))
				buffers_color[index].write(struct.pack("<f", loop[color_layer].color[2]))
				buffers_color[index].write(struct.pack("<f", loop[color_layer].color[3]))

			for index, uv_layer in enumerate(bm_uv_layers):
				buffers_uv[index].write(struct.pack("<f", loop[uv_layer].uv[0]))
				buffers_uv[index].write(struct.pack("<f", loop[uv_layer].uv[1]))

	# The face length buffer defines how many tris are actually the same face.
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

		buffer_tris_material_index.write(tri[0].face.material_index.to_bytes(length=split_indices_width, byteorder="little"))

		last_face_index = tri[0].face.index

	for face_len in face_lens:
		buffer_faces.write(face_len.to_bytes(length=4, byteorder="little"))

	# TODO export edges

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
	stf_mesh["buffer_tris_material_index"] = context.serialize_buffer(buffer_tris_material_index)
	stf_mesh["faces"] = context.serialize_buffer(buffer_faces)

	stf_mesh["uvs"] = []
	for buffer_uv in buffers_uv:
		stf_mesh["uvs"].append(context.serialize_buffer(buffer_uv))

	stf_mesh["colors"] = []
	for color_buffer in buffers_color:
		stf_mesh["colors"].append(context.serialize_buffer(color_buffer))

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
	bpy.types.Mesh.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Mesh.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Mesh.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Mesh, "stf_id"):
		del bpy.types.Mesh.stf_id
	if hasattr(bpy.types.Mesh, "stf_name"):
		del bpy.types.Mesh.stf_name
	if hasattr(bpy.types.Mesh, "stf_components"):
		del bpy.types.Mesh.stf_components
	if hasattr(bpy.types.Mesh, "stf_active_component_index"):
		del bpy.types.Mesh.stf_active_component_index

