from io import BytesIO
import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_translation_to_stf
from ...utils.buffer_utils import serialize_float, serialize_uint


_stf_type = "stf.mesh"


export_options: dict = {
	"export_normals": True,
	"export_tangents": True,
	"export_colors": True,
}


def export_stf_mesh(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
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

