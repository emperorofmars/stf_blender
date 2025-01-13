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
		py_vertices.append(stf_translation_to_blender([p0, p1, p2]))

	split_count = json_resource.get("split_count", 0)
	split_indices_width = json_resource.get("split_indices_width", 4)

	py_splits = []
	if(split_count > 0 and "splits" in json_resource):
		buffer_split = BytesIO(mesh_context.import_buffer(json_resource["splits"]))
		for index in range(split_count):
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
	if(blender_mesh.validate(verbose=True)): # return is True if errors found
		context.report(STFReport("Invalid mesh", STFReportSeverity.Error, id, _stf_type, blender_mesh))


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
		for index in range(len(json_resource["colors"])):
			color_attribute = blender_mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
			buffer_vertex_colors = BytesIO(mesh_context.import_buffer(json_resource["colors"][index]))
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

		if("uvs" in json_resource):
			split_uv_width = json_resource.get("split_uv_width", 4)
			for uv_layer_index in range(len(json_resource["uvs"])):
				uv_layer = blender_mesh.uv_layers.new(name=json_resource["uvs"][uv_layer_index].get("name", "UVMap"))
				buffer_uv = BytesIO(mesh_context.import_buffer(json_resource["uvs"][uv_layer_index]["uv"]))
				for index, loop in enumerate(blender_mesh.loops):
					# TODO convert uv from gltf uv coordinate space
					uv = [parse_float(buffer_uv, split_uv_width), parse_float(buffer_uv, split_uv_width)]
					uv_layer.uv[index].vector = uv

		if("split_colors" in json_resource):
			split_color_width = json_resource.get("split_color_width", 4)
			for index in range(len(json_resource["colors"])):
				color_attribute = blender_mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
				buffer_split_colors = BytesIO(mesh_context.import_buffer(json_resource["split_colors"][index]))
				for index, vertex in enumerate(blender_mesh.vertices):
					r = parse_float(buffer_split_colors, split_color_width)
					g = parse_float(buffer_split_colors, split_color_width)
					b = parse_float(buffer_split_colors, split_color_width)
					a = parse_float(buffer_split_colors, split_color_width)
					color_attribute.data[index].color = (r, g, b, a)

	return blender_mesh, mesh_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(context, blender_mesh)

	armature: bpy.types.Armature = parent_application_object

	stf_mesh = {
		"type": _stf_type,
		"name": blender_mesh.stf_name if blender_mesh.stf_name else blender_mesh.name,
	}
	mesh_context = STF_ResourceExportContext(context, stf_mesh, blender_mesh)

	default_materials = []
	for material in blender_mesh.materials:
		if(material):
			default_materials.append(mesh_context.serialize_resource(material))
		else:
			default_materials.append(None)
	stf_mesh["default_materials"] = default_materials

	float_width = 4
	vertex_indices_width = 4 if len(blender_mesh.vertices) * 3 < 2**32 else 8
	split_indices_width = 4 if len(blender_mesh.loops) * 3 < 2**32 else 8


	# vertices
	stf_mesh["vertex_count"] = len(blender_mesh.vertices)
	stf_mesh["vertex_width"] = float_width
	stf_mesh["vertex_indices_width"] = vertex_indices_width

	buffer_vertices = BytesIO()

	# Vertex positions
	for vertex in blender_mesh.vertices:
		position = blender_translation_to_stf(vertex.co)
		buffer_vertices.write(serialize_float(position[0], float_width))
		buffer_vertices.write(serialize_float(position[1], float_width))
		buffer_vertices.write(serialize_float(position[2], float_width))
	stf_mesh["vertices"] = mesh_context.serialize_buffer(buffer_vertices.getvalue())

	# Vertex normals
	stf_mesh["vertex_normal_width"] = float_width
	buffer_vertex_normals = BytesIO()
	for vertex in blender_mesh.vertices:
		normal = blender_translation_to_stf(vertex.normal)
		buffer_vertex_normals.write(serialize_float(normal[0], float_width))
		buffer_vertex_normals.write(serialize_float(normal[1], float_width))
		buffer_vertex_normals.write(serialize_float(normal[2], float_width))
	stf_mesh["vertex_normals"] = mesh_context.serialize_buffer(buffer_vertex_normals.getvalue())

	# Vertex color channels
	stf_mesh["vertex_color_width"] = float_width
	buffers_color: list[BytesIO] = []
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
	stf_mesh["colors"] = []
	for color_buffer in buffers_color:
		stf_mesh["colors"].append(mesh_context.serialize_buffer(color_buffer.getvalue()))

	# Splits
	stf_mesh["split_count"] = len(blender_mesh.loops)
	stf_mesh["split_indices_width"] = split_indices_width
	stf_mesh["split_normal_width"] = float_width
	stf_mesh["split_tangent_width"] = float_width
	stf_mesh["split_color_width"] = float_width
	stf_mesh["split_uv_width"] = float_width
	stf_mesh["split_uv_width"] = float_width

	buffer_split_vertices = BytesIO()
	buffer_split_normals = BytesIO()
	buffer_split_tangents = BytesIO()
	buffers_uv: list[BytesIO] = [BytesIO()] * len(blender_mesh.uv_layers)
	buffers_split_color: list[BytesIO] = []

	uv_names = []
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
			uv_names.append(uv_layer.name)
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

	stf_mesh["splits"] = mesh_context.serialize_buffer(buffer_split_vertices.getvalue())
	stf_mesh["split_normals"] = mesh_context.serialize_buffer(buffer_split_normals.getvalue())
	stf_mesh["split_tangents"] = mesh_context.serialize_buffer(buffer_split_tangents.getvalue())
	stf_mesh["uvs"] = []
	for index, buffer_uv in enumerate(buffers_uv):
		stf_mesh["uvs"].append({
				"name": uv_names[index],
				"uv": mesh_context.serialize_buffer(buffer_uv.getvalue()),
			})
	stf_mesh["split_colors"] = []
	for split_color_buffer in buffers_split_color:
		stf_mesh["split_colors"].append(mesh_context.serialize_buffer(split_color_buffer.getvalue()))


	# Triangles, faces, and their material indices
	stf_mesh["tris_count"] = len(blender_mesh.loop_triangles)
	stf_mesh["face_count"] = len(blender_mesh.polygons)
	face_width = stf_mesh["face_width"] = 4

	buffer_lines = BytesIO()
	buffer_tris = BytesIO()
	buffer_faces = BytesIO()

	# Loop through triangles, and also store how many belong to the same face
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

	stf_mesh["tris"] = mesh_context.serialize_buffer(buffer_tris.getvalue())

	# Material indices
	material_indices_width = stf_mesh["material_indices_width"] = 4
	buffer_face_material_indices = BytesIO()
	for index, polygon in enumerate(blender_mesh.polygons):
		buffer_faces.write(serialize_uint(face_lens[index], face_width))
		buffer_face_material_indices.write(serialize_uint(polygon.material_index, material_indices_width))
	stf_mesh["faces"] = mesh_context.serialize_buffer(buffer_faces.getvalue())
	stf_mesh["buffer_face_material_indices"] = mesh_context.serialize_buffer(buffer_face_material_indices.getvalue())


	# TODO also export edges if wanted


	# Weightpaint
	if(armature):
		stf_mesh["armature"] = mesh_context.serialize_resource(armature)

		# Index of the bone id corresponds to the bone index in every individual weight
		weight_bone_map = []
		for bone in armature.bones:
			weight_bone_map.append(bone.stf_id)
		stf_mesh["bones"] = weight_bone_map

		bone_weight_width = stf_mesh["bone_weight_width"] = 4
		bone_indices_width = stf_mesh["bone_indices_width"] = 4

		max_weight_group_count = 0
		weight_channels = []
		# For each vertex and each group of the vertex
		for vertex_index, vertex in enumerate(blender_mesh.vertices):
			if(len(vertex.groups) > max_weight_group_count): max_weight_group_count = len(vertex.groups)
			for group_index, group in enumerate(vertex.groups):
				try:
					bone_index = group.group
					bone_from_map = weight_bone_map[group.group]
				except Exception:
					continue
				if(bone_from_map):
					while(len(weight_channels) <= group_index): weight_channels.append([])
					weight_channels[group_index].append((vertex_index, bone_index, group.weight))

		# Convert weight arrays to buffers
		buffers_weights = []
		for group, weight_channel in enumerate(weight_channels):
			buffer_weights = BytesIO()
			indexed = len(weight_channel) < (len(blender_mesh.vertices) / 2)
			for weight in weight_channel:
				if(indexed): buffer_weights.write(serialize_uint(weight[0], vertex_indices_width)) # vertex index
				buffer_weights.write(serialize_uint(weight[1], bone_indices_width)) # bone index
				buffer_weights.write(serialize_float(weight[2], bone_weight_width)) # bone weight
			buffers_weights.append({
				"indexed": indexed,
				"count": len(weight_channel),
				"buffer": mesh_context.serialize_buffer(buffer_weights.getvalue())
			})
		stf_mesh["weights"] = buffers_weights


	groups = []
	# TODO vertex groups


	# for each blendshape and vertex
	buffer_blendshape_indices = BytesIO()
	buffer_blendshape_translation = BytesIO()
	buffer_blendshape_normal = BytesIO()
	buffer_blendshape_tangent = BytesIO()
	#for shape_key in blender_mesh.shape_keys.key_blocks:
	#	pass


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

