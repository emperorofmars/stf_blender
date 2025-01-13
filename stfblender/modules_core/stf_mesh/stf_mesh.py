from io import BytesIO
import bpy
import bmesh

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_translation_to_stf, stf_translation_to_blender
from ...utils.buffer_utils import parse_float, parse_uint, serialize_float, serialize_uint


_stf_type = "stf.mesh"


export_options: dict = {
	"export_colors": True,
	"optimize_mesh": False,
}


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_mesh = bpy.data.meshes.new(json_resource.get("name", "STF Mesh"))
	blender_mesh.stf_id = id
	blender_mesh.stf_name = json_resource.get("name", "STF Mesh")

	mesh_context = STF_ResourceImportContext(context, json_resource, blender_mesh)

	bm = bmesh.new()
	vertex_count = json_resource["vertex_count"]
	vertex_indices_width = json_resource.get("vertex_indices_width", 4)
	vertex_width = json_resource.get("vertex_width", 4)

	vertex_buffer = BytesIO(mesh_context.import_buffer(json_resource["vertices"]))
	for _ in range(vertex_count):
		p0 = parse_float(vertex_buffer, vertex_width)
		p1 = parse_float(vertex_buffer, vertex_width)
		p2 = parse_float(vertex_buffer, vertex_width)
		bm.verts.new(stf_translation_to_blender([p0, p1, p2]))

	bm.verts.index_update()
	bm.verts.ensure_lookup_table()

	split_count = json_resource.get("split_count", 0)

	split_indices_width = json_resource.get("split_indices_width", 4)
	split_normal_width = json_resource.get("split_normal_width", 4)
	split_tangent_width = json_resource.get("split_tangent_width", 4)
	split_color_width = json_resource.get("split_color_width", 4)
	split_uv_width = json_resource.get("split_uv_width", 4)

	tris_count = json_resource.get("tris_count", 0)
	face_count = json_resource.get("face_count", 0)
	face_width = json_resource.get("face_width", 0)

	if(split_count > 0 and "splits" in json_resource):
		split_buffer = BytesIO(mesh_context.import_buffer(json_resource["splits"]))
	if(split_count > 0 and "normals" in json_resource):
		normals_buffer = BytesIO(mesh_context.import_buffer(json_resource["normals"]))
	if(split_count > 0 and "tangents" in json_resource):
		tangents_buffer = BytesIO(mesh_context.import_buffer(json_resource["tangents"]))
	if(split_count > 0 and "tris" in json_resource):
		buffer_tris = BytesIO(mesh_context.import_buffer(json_resource["tris"]))
	if(face_count > 0 and "faces" in json_resource):
		buffer_faces = BytesIO(mesh_context.import_buffer(json_resource["faces"]))

	splits = []
	for _ in range(split_count):
		splits.append(parse_uint(split_buffer, vertex_indices_width))

	"""for _ in range(face_count):
		face_len = parse_uint(buffer_faces, face_width)
		face_splits = set()
		for _ in range(face_len):
			face_splits.add(parse_uint(buffer_tris, split_indices_width))
			face_splits.add(parse_uint(buffer_tris, split_indices_width))
			face_splits.add(parse_uint(buffer_tris, split_indices_width))

		face_verts = []
		for split in sorted(face_splits):
			face_verts.append(bm.verts[splits[split]])

		bm.faces.new(face_verts)"""

	for _ in range(face_count):
		face_len = parse_uint(buffer_faces, face_width)
		face_tris = []
		for _ in range(face_len):
			p0 = parse_uint(buffer_tris, split_indices_width)
			p1 = parse_uint(buffer_tris, split_indices_width)
			p2 = parse_uint(buffer_tris, split_indices_width)
			face_tris.append(bm.faces.new([bm.verts[splits[p0]], bm.verts[splits[p1]], bm.verts[splits[p2]]]))

		if(len(face_tris) > 1):
			bmesh.utils.face_join(face_tris, True)

	bm.edges.index_update()
	bm.faces.index_update()

	bm.to_mesh(blender_mesh)

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
		"vertex_width": float_width,
		"vertex_indices_width": vertex_indices_width,
		"split_indices_width": split_indices_width,
		"split_normal_width": float_width,
		"split_tangent_width": float_width,
		"split_color_width": float_width,
		"split_uv_width": float_width,
		"tris_count": len(bm_tris),
	}

	mesh_context = STF_ResourceExportContext(context, stf_mesh, blender_mesh)

	# The vertices only store the position. Normals, uv's, etc... are stored in splits. The vertex is here to inform the application that these many splits are actually the same point.
	# Vertices get targeted by weights and blendshapes.
	# Splits get targeted by polygons/faces.
	buffer_vertices = BytesIO()
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

	bm_uv_layers = bm.loops.layers.uv
	buffers_uv: list[BytesIO] = [BytesIO()] * len(bm_uv_layers)

	bm_color_layers = bm.loops.layers.color
	buffers_color: list[BytesIO] = [BytesIO()] * len(bm_color_layers)

	split_count = 0
	for face in bm.faces:
		for loop in face.loops:
			# Splits reference the 'real' vertex by index. The normal, tangent, uv, etc... indices correspond to the split vertices index.
			buffer_split_vertices.write(serialize_uint(loop.vert.index, vertex_indices_width))

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

			split_count += 1

	stf_mesh["split_count"] = split_count

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

	face_width = 4
	for face_len in face_lens:
		buffer_faces.write(serialize_uint(face_len, face_width))


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

	stf_mesh["face_count"] = len(face_lens)
	stf_mesh["face_width"] = face_width

	stf_mesh["vertices"] = mesh_context.serialize_buffer(buffer_vertices.getvalue())
	stf_mesh["splits"] = mesh_context.serialize_buffer(buffer_split_vertices.getvalue())
	stf_mesh["normals"] = mesh_context.serialize_buffer(buffer_normals.getvalue())
	stf_mesh["tangents"] = mesh_context.serialize_buffer(buffer_tangents.getvalue())
	stf_mesh["tris"] = mesh_context.serialize_buffer(buffer_tris.getvalue())
	stf_mesh["buffer_tris_material_index"] = mesh_context.serialize_buffer(buffer_tris_material_index.getvalue())
	stf_mesh["faces"] = mesh_context.serialize_buffer(buffer_faces.getvalue())

	stf_mesh["uvs"] = []
	for buffer_uv in buffers_uv:
		stf_mesh["uvs"].append(mesh_context.serialize_buffer(buffer_uv.getvalue()))

	stf_mesh["colors"] = []
	for color_buffer in buffers_color:
		stf_mesh["colors"].append(mesh_context.serialize_buffer(color_buffer.getvalue()))

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

