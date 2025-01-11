from io import BytesIO
import struct
import bpy
import bmesh

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_translation_to_stf
from ...utils.buffer_utils import serialize_float, serialize_uint


_stf_type = "stf.mesh"


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any, import_hook_results: list[any]) -> tuple[any, any]:
	blender_mesh = bpy.data.meshes.new(json_resource.get("name", "STF Mesh"))
	blender_mesh.stf_id = id
	blender_mesh.stf_name = json_resource.get("name", "STF Mesh")

	#hook_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_mesh)

	mesh_context = STF_ResourceImportContext(context, json_resource, blender_mesh)

	# TODO
	return blender_mesh, mesh_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(context, blender_mesh)

	bm = bmesh.new()
	bm.from_mesh(blender_mesh)
	bm.verts.index_update()
	bm.edges.index_update()
	bm.faces.index_update()

	bm_tris: list[tuple[bmesh.types.BMLoop, bmesh.types.BMLoop, bmesh.types.BMLoop]] = bm.calc_loop_triangles()

	vertex_indices_width = 4 if len(bm.verts) * 3 < 2**32 else 8
	split_indices_width = 4 if len(bm_tris) * 3 < 2**32 else 8
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

	mesh_context = STF_ResourceExportContext(context, stf_mesh, blender_mesh)

	buffer_vertices = BytesIO()
	# The vertex only stores the position. Normals, uv's, etc... are stored by split vertices. The vertex is here to inform the application that these many split vertices are actually the same point.
	for vertex in bm.verts:
		position = blender_translation_to_stf(vertex.co)
		buffer_vertices.write(serialize_float(position[0], float_width))
		buffer_vertices.write(serialize_float(position[1], float_width))
		buffer_vertices.write(serialize_float(position[2], float_width))

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
			buffer_normals.write(serialize_float(normal[0], float_width))
			buffer_normals.write(serialize_float(normal[1], float_width))
			buffer_normals.write(serialize_float(normal[2], float_width))

			tangent = blender_translation_to_stf(loop.calc_tangent())
			buffer_tangents.write(serialize_float(tangent[0], float_width))
			buffer_tangents.write(serialize_float(tangent[1], float_width))
			buffer_tangents.write(serialize_float(tangent[2], float_width))

			for index, color_layer in enumerate(bm_color_layers):
				buffers_color[index].write(serialize_float(loop[color_layer].color[0], float_width))
				buffers_color[index].write(serialize_float(loop[color_layer].color[1], float_width))
				buffers_color[index].write(serialize_float(loop[color_layer].color[2], float_width))
				buffers_color[index].write(serialize_float(loop[color_layer].color[3], float_width))

			for index, uv_layer in enumerate(bm_uv_layers):
				buffers_uv[index].write(serialize_float(loop[uv_layer].uv[0], float_width))
				buffers_uv[index].write(serialize_float(loop[uv_layer].uv[1], float_width))

	# The face length buffer defines how many tris are actually the same face.
	face_lens: list[int] = [0]
	last_face_index = 0
	for tri in bm_tris:
		if(last_face_index == tri[0].face.index):
			face_lens[len(face_lens) - 1] += 1
		else:
			face_lens.append(1)

		buffer_tris.write(serialize_uint(tri[0].index, split_indices_width))
		buffer_tris.write(serialize_uint(tri[1].index, split_indices_width))
		buffer_tris.write(serialize_uint(tri[2].index, split_indices_width))

		buffer_tris_material_index.write(serialize_uint(tri[0].face.material_index, split_indices_width))
		last_face_index = tri[0].face.index

	for face_len in face_lens:
		buffer_faces.write(serialize_uint(face_len, 4))

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


	stf_mesh["vertices"] = mesh_context.serialize_buffer(buffer_vertices)
	stf_mesh["splits"] = mesh_context.serialize_buffer(buffer_split_vertices)
	stf_mesh["normals"] = mesh_context.serialize_buffer(buffer_normals)
	stf_mesh["tangents"] = mesh_context.serialize_buffer(buffer_tangents)
	stf_mesh["tris"] = mesh_context.serialize_buffer(buffer_tris)
	stf_mesh["buffer_tris_material_index"] = mesh_context.serialize_buffer(buffer_tris_material_index)
	stf_mesh["faces"] = mesh_context.serialize_buffer(buffer_faces)

	stf_mesh["uvs"] = []
	for buffer_uv in buffers_uv:
		stf_mesh["uvs"].append(mesh_context.serialize_buffer(buffer_uv))

	stf_mesh["colors"] = []
	for color_buffer in buffers_color:
		stf_mesh["colors"].append(mesh_context.serialize_buffer(color_buffer))

	return stf_mesh, blender_mesh.stf_id, mesh_context


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

