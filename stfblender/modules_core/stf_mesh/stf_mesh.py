from io import BytesIO
import mathutils
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
	"export_tangents": True,
}


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_mesh = bpy.data.meshes.new(json_resource.get("name", "STF Mesh"))
	blender_mesh.stf_id = id
	blender_mesh.stf_name = json_resource.get("name", "STF Mesh")

	mesh_context = STF_ResourceImportContext(context, json_resource, blender_mesh)

	vertex_count = json_resource["vertex_count"]
	vertex_indices_width = json_resource.get("vertex_indices_width", 4)
	vertex_width = json_resource.get("vertex_width", 4)

	buffer_vertices = BytesIO(mesh_context.import_buffer(json_resource["vertices"]))
	py_vertices = []
	for _ in range(vertex_count):
		p0 = parse_float(buffer_vertices, vertex_width)
		p1 = parse_float(buffer_vertices, vertex_width)
		p2 = parse_float(buffer_vertices, vertex_width)
		#bm.verts.new(stf_translation_to_blender([p0, p1, p2]))
		py_vertices.append(stf_translation_to_blender([p0, p1, p2]))

	split_count = json_resource.get("split_count", 0)
	split_indices_width = json_resource.get("split_indices_width", 4)

	split_color_width = json_resource.get("split_color_width", 4)
	split_uv_width = json_resource.get("split_uv_width", 4)

	py_splits = []
	if(split_count > 0 and "splits" in json_resource):
		buffer_split = BytesIO(mesh_context.import_buffer(json_resource["splits"]))
		#blender_mesh.loops.add(split_count)
		for index in range(split_count):
			#loop.vertex_index = parse_uint(buffer_split, vertex_indices_width)
			py_splits.append(parse_uint(buffer_split, vertex_indices_width))

	py_faces = []
	tris_count = json_resource.get("tris_count", 0)
	face_count = json_resource.get("face_count", 0)
	if(face_count > 0):
		face_width = json_resource.get("face_width", 0)
		buffer_faces = BytesIO(mesh_context.import_buffer(json_resource["faces"]))
		buffer_tris = BytesIO(mesh_context.import_buffer(json_resource["tris"]))

		for index in range(face_count):
			face_len = parse_uint(buffer_faces, face_width)
			face_splits = set()
			for _ in range(face_len):
				face_splits.add(parse_uint(buffer_tris, split_indices_width))
				face_splits.add(parse_uint(buffer_tris, split_indices_width))
				face_splits.add(parse_uint(buffer_tris, split_indices_width))

			face_indices = []
			for split_index in sorted(face_splits):
				face_indices.append(py_splits[split_index])
			py_faces.append(face_indices)

	elif(tris_count > 0):
		buffer_tris = BytesIO(mesh_context.import_buffer(json_resource["tris"]))
		for index in range(tris_count):
			face_splits = set()
			for _ in range(3):
				face_splits.add(parse_uint(buffer_tris, split_indices_width))
				face_splits.add(parse_uint(buffer_tris, split_indices_width))
				face_splits.add(parse_uint(buffer_tris, split_indices_width))

			face_indices = []
			for split_index in sorted(face_splits):
				face_indices.append(py_splits[split_index])
			py_faces.append(face_indices)


	blender_mesh.from_pydata(py_vertices, [], py_faces)
	# TODO validate


	if("normals" in json_resource):
		vertex_normals_width = json_resource.get("vertex_normals_width", 4)
		buffer_vertex_normals = BytesIO(mesh_context.import_buffer(json_resource["normals"]))
		for index, vertex in enumerate(blender_mesh.vertices):
			p0 = parse_float(buffer_vertex_normals, vertex_normals_width)
			p1 = parse_float(buffer_vertex_normals, vertex_normals_width)
			p2 = parse_float(buffer_vertex_normals, vertex_normals_width)
			vertex.normal = stf_translation_to_blender([p0, p1, p2])

	if("colors" in json_resource):
		vertex_color_width = json_resource.get("vertex_color_width", 4)
		print(json_resource["colors"])
		print("vertex_color_width: " + str(vertex_color_width))

		color_attribute = blender_mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
		for index in range(len(json_resource["colors"])):
			buffer_vertex_colors = BytesIO(mesh_context.import_buffer(json_resource["colors"][index]))
			print(len(buffer_vertex_colors.getvalue()))
			for index, vertex in enumerate(blender_mesh.vertices):
				r = parse_float(buffer_vertex_colors, vertex_color_width)
				g = parse_float(buffer_vertex_colors, vertex_color_width)
				b = parse_float(buffer_vertex_colors, vertex_color_width)
				a = parse_float(buffer_vertex_colors, vertex_color_width)
				color_attribute.data[index].color = (r, g, b, a)


	if(split_count > 0 and "splits" in json_resource):
		if("split_normals" in json_resource):
			split_normal_width = json_resource.get("split_normal_width", 4)
			buffer_split_normals = BytesIO(mesh_context.import_buffer(json_resource["split_normals"]))
			py_split_normals = []
			for index, loop in enumerate(blender_mesh.loops):
				normal = stf_translation_to_blender([parse_float(buffer_split_normals, split_normal_width), parse_float(buffer_split_normals, split_normal_width), parse_float(buffer_split_normals, split_normal_width)])
				py_split_normals.append(normal)
			blender_mesh.normals_split_custom_set(py_split_normals)

		"""if("split_tangents" in json_resource):
			split_tangent_width = json_resource.get("split_tangent_width", 4)
			buffer_split_tangents = BytesIO(mesh_context.import_buffer(json_resource["split_tangents"]))
			for index, loop in enumerate(blender_mesh.loops):
				pass"""

		# TODO uvs, colors"""


	return blender_mesh, mesh_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(context, blender_mesh)

	stf_mesh = {
		"type": _stf_type,
		"name": blender_mesh.stf_name if blender_mesh.stf_name else blender_mesh.name,
	}
	mesh_context = STF_ResourceExportContext(context, stf_mesh, blender_mesh)

	float_width = 4
	vertex_indices_width = 4 if len(blender_mesh.vertices) * 3 < 2**32 else 8
	split_indices_width = 4 if len(blender_mesh.loops) * 3 < 2**32 else 8

	buffer_vertices = BytesIO()
	buffer_vertex_normals = BytesIO()

	buffers_color: list[BytesIO] = []

	buffer_split_vertices = BytesIO()
	buffer_split_normals = BytesIO()
	buffer_split_tangents = BytesIO()
	buffers_uv: list[BytesIO] = [BytesIO()] * len(blender_mesh.uv_layers)
	buffers_split_color: list[BytesIO] = []

	buffer_lines = BytesIO()
	buffer_tris = BytesIO()
	buffer_face_material_indices = BytesIO()
	buffer_faces = BytesIO()

	# for each weight channel and vertex
	buffer_weights_indices = BytesIO()
	buffer_weights_target = BytesIO()
	buffer_weights = BytesIO()

	# for each blendshape and vertex
	buffer_blendshape_indices = BytesIO()
	buffer_blendshape_translation = BytesIO()
	buffer_blendshape_normal = BytesIO()
	buffer_blendshape_tangent = BytesIO()


	for vertex in blender_mesh.vertices:
		position = blender_translation_to_stf(vertex.co)
		buffer_vertices.write(serialize_float(position[0], float_width))
		buffer_vertices.write(serialize_float(position[1], float_width))
		buffer_vertices.write(serialize_float(position[2], float_width))

		normal = blender_translation_to_stf(vertex.normal)
		buffer_vertex_normals.write(serialize_float(normal[0], float_width))
		buffer_vertex_normals.write(serialize_float(normal[1], float_width))
		buffer_vertex_normals.write(serialize_float(normal[2], float_width))

	for index, color_layer in enumerate(blender_mesh.color_attributes):
		if(color_layer.data_type == "FLOAT_COLOR" and color_layer.domain == "POINT"):
			color_buffer = BytesIO()
			buffers_color.append(color_buffer)
			for vertex in blender_mesh.vertices:
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[0], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[1], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[2], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[3], float_width))
		# TODO other data types

	for loop in blender_mesh.loops:
		loop: bpy.types.MeshLoop = loop
		buffer_split_vertices.write(serialize_uint(loop.vertex_index, vertex_indices_width))

		normal = blender_translation_to_stf(loop.normal)
		buffer_split_normals.write(serialize_float(normal[0], float_width))
		buffer_split_normals.write(serialize_float(normal[1], float_width))
		buffer_split_normals.write(serialize_float(normal[2], float_width))

		tangent = blender_translation_to_stf(loop.tangent)
		buffer_split_tangents.write(serialize_float(tangent[0], float_width))
		buffer_split_tangents.write(serialize_float(tangent[1], float_width))
		buffer_split_tangents.write(serialize_float(tangent[2], float_width))

		for index, uv_layer in enumerate(blender_mesh.uv_layers):
			buffers_uv[index].write(serialize_float(uv_layer.uv[loop.index].vector[0], float_width))
			buffers_uv[index].write(serialize_float(uv_layer.uv[loop.index].vector[1], float_width))

	for index, color_layer in enumerate(blender_mesh.color_attributes):
		if(color_layer.data_type == "FLOAT_COLOR" and color_layer.domain == "CORNER"):
			color_buffer = BytesIO()
			buffers_split_color.append(color_buffer)
			for vertex in blender_mesh.vertices:
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[0], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[1], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[2], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[3], float_width))
		# TODO other data types


	face_width = 4
	face_lens: list[int] = [0]
	last_face_index = 0
	blender_mesh.calc_loop_triangles()
	for tris in blender_mesh.loop_triangles:
		if(last_face_index == tris.polygon_index):
			face_lens[len(face_lens) - 1] += 1
		else:
			face_lens.append(1)
		for split_index in tris.loops:
			buffer_tris.write(serialize_uint(split_index, split_indices_width))
		last_face_index = tris.polygon_index

	material_indices_width = 4
	for index, polygon in enumerate(blender_mesh.polygons):
		buffer_faces.write(serialize_uint(face_lens[index], face_width))
		buffer_face_material_indices.write(serialize_uint(polygon.material_index, material_indices_width))


	# TODO export edges


	stf_mesh["vertex_count"] = len(blender_mesh.vertices)
	stf_mesh["split_count"] = len(blender_mesh.loops)
	stf_mesh["tris_count"] = len(blender_mesh.loop_triangles)
	stf_mesh["face_count"] = len(blender_mesh.polygons)

	stf_mesh["vertex_indices_width"] = vertex_indices_width
	stf_mesh["split_indices_width"] = split_indices_width
	stf_mesh["material_indices_width"] = material_indices_width
	stf_mesh["face_width"] = face_width

	stf_mesh["vertex_width"] = float_width
	stf_mesh["vertex_normal_width"] = float_width
	stf_mesh["vertex_color_width"] = float_width
	stf_mesh["split_normal_width"] = float_width
	stf_mesh["split_tangent_width"] = float_width
	stf_mesh["split_color_width"] = float_width
	stf_mesh["split_uv_width"] = float_width
	stf_mesh["split_uv_width"] = float_width


	stf_mesh["vertices"] = mesh_context.serialize_buffer(buffer_vertices.getvalue())
	stf_mesh["vertex_normals"] = mesh_context.serialize_buffer(buffer_vertex_normals.getvalue())
	stf_mesh["colors"] = []
	for color_buffer in buffers_color:
		stf_mesh["colors"].append(mesh_context.serialize_buffer(color_buffer.getvalue()))

	stf_mesh["splits"] = mesh_context.serialize_buffer(buffer_split_vertices.getvalue())
	stf_mesh["split_normals"] = mesh_context.serialize_buffer(buffer_split_normals.getvalue())
	stf_mesh["split_tangents"] = mesh_context.serialize_buffer(buffer_split_tangents.getvalue())
	stf_mesh["uvs"] = []
	for buffer_uv in buffers_uv:
		stf_mesh["uvs"].append(mesh_context.serialize_buffer(buffer_uv.getvalue()))
	stf_mesh["split_colors"] = []
	for split_color_buffer in buffers_split_color:
		stf_mesh["split_colors"].append(mesh_context.serialize_buffer(split_color_buffer.getvalue()))

	stf_mesh["tris"] = mesh_context.serialize_buffer(buffer_tris.getvalue())
	stf_mesh["faces"] = mesh_context.serialize_buffer(buffer_faces.getvalue())
	stf_mesh["buffer_face_material_indices"] = mesh_context.serialize_buffer(buffer_face_material_indices.getvalue())

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

