from io import BytesIO
import bpy
import bmesh

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import blender_translation_to_stf
from ...utils.buffer_utils import serialize_float, serialize_int, serialize_uint


_stf_type = "stf.mesh"


export_options: dict = {
	"export_normals": True,
	"export_tangents": True,
	"export_colors": True,
}


def export_stf_mesh(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(context, blender_mesh)

	if(parent_application_object and len(parent_application_object) == 2):
		armature: bpy.types.Armature = parent_application_object[0]
		blender_mesh_object: bpy.types.Object = parent_application_object[1]


	stf_mesh = {
		"type": _stf_type,
		"name": blender_mesh.stf_name if blender_mesh.stf_name else blender_mesh.name,
	}
	mesh_context = STF_ResourceExportContext(context, stf_mesh, blender_mesh)

	material_slots = []
	for material in blender_mesh.materials:
		if(material):
			material_slots.append(mesh_context.serialize_resource(material))
		else:
			material_slots.append(None)
	stf_mesh["material_slots"] = material_slots

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

	# Face corners (Splits)
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
		# Split to vertex indices
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
	stf_mesh["material_indices"] = mesh_context.serialize_buffer(buffer_face_material_indices.getvalue())


	# TODO also export edges if wanted


	# Weightpaint
	if(armature and blender_mesh_object):
		stf_mesh["armature"] = mesh_context.serialize_resource(armature)

		# Create vertex group lookup dictionary for stf_ids from the previous name lookup dict
		weight_bone_map = []
		group_to_bone_index = {}
		for group in blender_mesh_object.vertex_groups:
			if(group.name in armature.bones):
				weight_bone_map.append(armature.bones[group.name].stf_id)
				group_to_bone_index[group.index] = len(weight_bone_map) - 1

		groups: dict[int, dict[int, float]] = {index: {} for index, _ in enumerate(weight_bone_map)}
		for vertex in blender_mesh.vertices:
			for group in vertex.groups:
				if(group.group in group_to_bone_index):
					groups[group_to_bone_index[group.group]][vertex.index] = group.weight

		bone_weight_width = stf_mesh["bone_weight_width"] = 4
		buffers_weights = []
		for bone_index, group in groups.items():
			indexed = len(group) < (len(blender_mesh.vertices) / 2)
			buffer_weights = BytesIO()
			if(indexed):
				for vertex_index, weight in group.items():
					buffer_weights.write(serialize_uint(vertex_index, vertex_indices_width)) # vertex index
					buffer_weights.write(serialize_float(weight, bone_weight_width)) # bone weight
			else:
				for vertex in blender_mesh.vertices:
					if(vertex.index in group):
						buffer_weights.write(serialize_float(group[vertex.index], bone_weight_width)) # bone weight
					else:
						buffer_weights.write(serialize_float(0, bone_weight_width)) # bone weight

			buffers_weights.append({
				"target_bone": weight_bone_map[bone_index],
				"indexed": indexed,
				"count": len(group) if indexed else len(blender_mesh.vertices),
				"buffer": mesh_context.serialize_buffer(buffer_weights.getvalue()),
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

