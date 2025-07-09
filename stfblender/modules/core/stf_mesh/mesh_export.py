from io import BytesIO
import bpy
import numpy as np

from ....exporter.stf_export_context import STF_ExportContext
from ....utils.id_utils import ensure_stf_id
from ....utils.trs_utils import blender_translation_to_stf, blender_uv_to_stf
from ....core.buffer_utils import determine_pack_format_float, determine_pack_format_uint, serialize_float, serialize_int, serialize_uint


_stf_type = "stf.mesh"


export_options: dict = {
	"export_normals": True,
	"export_tangents": True,
	"export_colors": True,
	"float_treshhold_blendshape": 0.00001,
}


# Mesh import and export are the lowest hanging fruits for performance improvements.

def export_stf_mesh(context: STF_ExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str]:
	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(context, blender_mesh)

	armature: bpy.types.Armature = parent_application_object

	tmp_blender_mesh_object: bpy.types.Object = bpy.data.objects.new("TRASH", blender_mesh)
	bpy.context.scene.collection.objects.link(tmp_blender_mesh_object)
	def _clean_tmp_mesh_object():
		bpy.data.objects.remove(tmp_blender_mesh_object)
	context.add_cleanup_task(_clean_tmp_mesh_object)

	blender_mesh.calc_loop_triangles()

	stf_mesh = {
		"type": _stf_type,
		"name": blender_mesh.stf_name if blender_mesh.stf_name_source_of_truth else blender_mesh.name,
	}

	material_slots = []
	for material in blender_mesh.materials:
		if(material):
			material_slots.append(context.serialize_resource(material))
		else:
			material_slots.append(None)
	stf_mesh["material_slots"] = material_slots

	float_width = 4

	max_len_indices = max(len(blender_mesh.loops), len(blender_mesh.polygons))
	## let indices_width
	if(max_len_indices <= 2**8):
		indices_width = 1
	elif(max_len_indices <= 2**16):
		indices_width = 2
	elif(max_len_indices <= 2**32):
		indices_width = 4
	elif(max_len_indices <= 2**64):
		indices_width = 8

	stf_mesh["float_width"] = float_width
	stf_mesh["indices_width"] = indices_width

	# Vertex positions
	buffer_vertices = np.zeros(len(blender_mesh.vertices) * 3, dtype=determine_pack_format_float(float_width))
	blender_mesh.vertices.foreach_get("co", buffer_vertices)
	buffer_vertices = np.reshape(buffer_vertices, (-1, 3))
	buffer_vertices[:, [1, 2]] = buffer_vertices[:, [2, 1]]
	buffer_vertices[:, 2] *= -1
	stf_mesh["vertices"] = context.serialize_buffer(buffer_vertices.tobytes())

	# Vertex color channels
	# todo use numpy
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
		elif(color_layer.data_type == "BYTE_COLOR" and color_layer.domain == "POINT"): # TODO deal with byte_color vs float_color actually
			color_buffer = BytesIO()
			buffers_color.append(color_buffer)
			for vertex in blender_mesh.vertices:
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[0], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[1], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[2], float_width))
				color_buffer.write(serialize_float(color_layer.data[vertex.index].color[3], float_width))
	stf_mesh["colors"] = []
	for color_buffer in buffers_color:
		stf_mesh["colors"].append(context.serialize_buffer(color_buffer.getvalue()))

	# splits
	buffer_split_vertices = np.zeros(len(blender_mesh.loops), dtype=determine_pack_format_uint(indices_width))
	blender_mesh.loops.foreach_get("vertex_index", buffer_split_vertices)
	stf_mesh["splits"] = context.serialize_buffer(buffer_split_vertices.tobytes())

	# normals
	buffer_split_normals = np.zeros(len(blender_mesh.loops) * 3, dtype=determine_pack_format_float(float_width))
	blender_mesh.loops.foreach_get("normal", buffer_split_normals)
	buffer_split_normals = np.reshape(buffer_split_normals, (-1, 3))
	buffer_split_normals[:, [1, 2]] = buffer_split_normals[:, [2, 1]]
	buffer_split_normals[:, 2] *= -1
	stf_mesh["split_normals"] = context.serialize_buffer(buffer_split_normals.tobytes())

	# uvs
	uvs = []
	for uv_index, uv_layer in enumerate(blender_mesh.uv_layers):
		buffer_uv = np.zeros(len(blender_mesh.loops) * 2, dtype=determine_pack_format_float(float_width))
		uv_layer.uv.foreach_get("vector", buffer_uv)
		buffer_uv = np.reshape(buffer_uv, (-1, 2))
		buffer_uv[:, 1] = 1 - buffer_uv[:, 1]
		uvs.append({"name": uv_layer.name, "uv": context.serialize_buffer(buffer_uv.tobytes())})
	stf_mesh["uvs"] = uvs

	# split colors
	buffers_split_color: list[BytesIO] = []
	for color_layer in blender_mesh.color_attributes:
		if(color_layer.data_type == "FLOAT_COLOR" and color_layer.domain == "CORNER"):
			color_buffer = BytesIO()
			buffers_split_color.append(color_buffer)
			for loop in blender_mesh.loops:
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[0], float_width))
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[1], float_width))
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[2], float_width))
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[3], float_width))
		elif(color_layer.data_type == "BYTE_COLOR" and color_layer.domain == "CORNER"): # TODO deal with byte_color vs float_color actually
			color_buffer = BytesIO()
			buffers_split_color.append(color_buffer)
			for loop in blender_mesh.loops:
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[0], float_width))
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[1], float_width))
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[2], float_width))
				color_buffer.write(serialize_float(color_layer.data[loop.index].color[3], float_width))

	stf_mesh["split_colors"] = []
	for split_color_buffer in buffers_split_color:
		stf_mesh["split_colors"].append(context.serialize_buffer(split_color_buffer.getvalue()))

	# topology
	buffer_tris = BytesIO()

	# Loop through triangles, and also store how many belong to the same face
	face_lens: list[int] = [0]
	last_face_index = 0
	for tris in blender_mesh.loop_triangles:
		if(last_face_index == tris.polygon_index):
			face_lens[len(face_lens) - 1] += 1
		else:
			face_lens.append(1)
		for split_index in tris.loops:
			buffer_tris.write(serialize_uint(split_index, indices_width))
		last_face_index = tris.polygon_index

	stf_mesh["tris"] = context.serialize_buffer(buffer_tris.getvalue())

	# Material indices and face sharpness
	buffer_flat_face_indices = BytesIO()
	flat_face_indices_len = 0
	buffer_faces = BytesIO()

	## let material_indices_width
	if(len(blender_mesh.materials) < 2**8):
		material_indices_width = 1
	elif(len(blender_mesh.materials) < 2**16):
		material_indices_width = 2
	# else wtf
	stf_mesh["material_indices_width"] = material_indices_width
	buffer_face_material_indices = BytesIO()
	for polygon in blender_mesh.polygons:
		buffer_faces.write(serialize_uint(face_lens[polygon.index], indices_width))
		buffer_face_material_indices.write(serialize_uint(polygon.material_index, material_indices_width))
		if(not polygon.use_smooth):
			flat_face_indices_len += 1
			buffer_flat_face_indices.write(serialize_uint(polygon.index, indices_width)) # this could be done better

	stf_mesh["faces"] = context.serialize_buffer(buffer_faces.getvalue())
	stf_mesh["material_indices"] = context.serialize_buffer(buffer_face_material_indices.getvalue())
	stf_mesh["sharp_face_indices"] = context.serialize_buffer(buffer_flat_face_indices.getvalue())


	# Lines (Edges not part of faces)
	buffer_lines = BytesIO()
	lines_len = 0
	for edge in blender_mesh.edges:
		if(edge.is_loose):
			lines_len += 1
			for edge_vertex_index in edge.vertices:
				buffer_lines.write(serialize_uint(edge_vertex_index, indices_width))
	stf_mesh["lines"] = context.serialize_buffer(buffer_lines.getvalue())


	# explicit edge sharpness
	buffer_sharp_edges = BytesIO()
	shapr_edges_len = 0
	for edge in blender_mesh.edges:
		if(edge.use_edge_sharp and not edge.is_loose):
			shapr_edges_len += 1
			for edge_vertex_index in edge.vertices:
				buffer_sharp_edges.write(serialize_uint(edge_vertex_index, indices_width))
	stf_mesh["sharp_edges"] = context.serialize_buffer(buffer_sharp_edges.getvalue())


	# TODO explicit single vertex sharpness at some point Blender plz


	# Weightpaint
	if(armature and tmp_blender_mesh_object):
		stf_mesh["armature"] = context.serialize_resource(armature)

		# Create vertex group lookup dictionary for stf_ids
		weight_bone_map = []
		group_to_bone_index = {}
		for group in tmp_blender_mesh_object.vertex_groups:
			if(group.name in armature.bones):
				weight_bone_map.append(armature.bones[group.name].stf_id)
				group_to_bone_index[group.index] = len(weight_bone_map) - 1
		stf_mesh["bones"] = weight_bone_map

		# TODO make this vertex-major and sort channels per vertex by weight
		# dict[channel_index, dict[vertex_index, tuple[bone_index, weight]]]
		bone_channels: dict[int, dict[int, tuple[int, float]]] = {}
		for vertex in blender_mesh.vertices:
			for channel, group in enumerate(vertex.groups):
				if(group.group in group_to_bone_index):
					if(channel not in bone_channels): bone_channels[channel] = {}
					bone_channels[channel][vertex.index] = (group_to_bone_index[group.group], group.weight)

		## let bone_indices_width
		if(len(bone_channels) <= 2**8):
			bone_indices_width = 1
		elif(len(bone_channels) <= 2**16):
			bone_indices_width = 2
		## else wtf
		stf_mesh["bone_indices_width"] = bone_indices_width

		buffers_weights = []
		for channel_index, channel in bone_channels.items():
			indexed = len(channel) < (len(blender_mesh.vertices) * 0.666)
			buffer_weights = BytesIO()
			if(indexed):
				for vertex_index, data in channel.items():
					buffer_weights.write(serialize_uint(vertex_index, indices_width)) # vertex index
					buffer_weights.write(serialize_int(data[0], bone_indices_width)) # bone index
					buffer_weights.write(serialize_float(data[1], float_width)) # bone weight
			else:
				for vertex in blender_mesh.vertices:
					if(vertex.index in channel):
						buffer_weights.write(serialize_int(channel[vertex.index][0], bone_indices_width)) # bone index
						buffer_weights.write(serialize_float(channel[vertex.index][1], float_width)) # bone weight
					else:
						buffer_weights.write(serialize_int(-1, bone_indices_width)) # bone index
						buffer_weights.write(serialize_float(0, float_width)) # bone weight

			buffers_weights.append({
				"indexed": indexed,
				"count": len(channel) if indexed else len(blender_mesh.vertices),
				"buffer": context.serialize_buffer(buffer_weights.getvalue()),
			})

		stf_mesh["weights"] = buffers_weights


	# Vertex groups
	if(tmp_blender_mesh_object):
		group_index_to_group_name: dict[int, str] = {}
		vertex_groups: dict[str, dict[int, float]] = {}
		for group in tmp_blender_mesh_object.vertex_groups:
			if(not armature or group.name not in armature.bones): # don't include weight paint groups
				vertex_groups[group.name] = {}
				group_index_to_group_name[group.index] = group.name

		if(len(vertex_groups) > 0):
			for vertex in blender_mesh.vertices:
				for group in vertex.groups:
					if(group.group in group_index_to_group_name):
						vertex_groups[group_index_to_group_name[group.group]][vertex.index] = group.weight

			buffers_vertex_groups = []

			for vertex_group_name, group in vertex_groups.items():
				indexed = len(group) < (len(blender_mesh.vertices) / 2)
				buffer_weights = BytesIO()
				if(indexed):
					for vertex_index, weight in group.items():
						buffer_weights.write(serialize_uint(vertex_index, indices_width)) # vertex index
						buffer_weights.write(serialize_float(weight, float_width)) # vertex weight
				else:
					for vertex in blender_mesh.vertices:
						if(vertex.index in group):
							buffer_weights.write(serialize_float(group[vertex.index], float_width)) # vertex weight
						else:
							buffer_weights.write(serialize_float(0, float_width)) # vertex weight

				buffers_vertex_groups.append({
					"name": vertex_group_name,
					"indexed": indexed,
					"count": len(group) if indexed else len(blender_mesh.vertices),
					"buffer": context.serialize_buffer(buffer_weights.getvalue()),
				})
			stf_mesh["vertex_groups"] = buffers_vertex_groups


	# Blendshapes / Morphtargets / Shapekeys / Blendtargets / Targetblends / Targetshapes / Morphshapes / Blendkeys / Shapetargets / Shapemorphs / Blendmorphs / Blendtargets / Morphblends / Morphkeys / Shapeblends / Blendblends / ...
	if(blender_mesh.shape_keys):
		blendshapes = []

		for shape_key in blender_mesh.shape_keys.key_blocks:
			if(shape_key == shape_key.relative_key or shape_key.mute or blender_mesh.shape_keys.key_blocks[0].name == shape_key.name):
				continue

			# TODO deal with vertex group multiplication maybe at some point

			blendshape_offsets_buffer = np.zeros(len(blender_mesh.vertices) * 3, dtype=determine_pack_format_float(float_width))
			shape_key.data.foreach_get("co", blendshape_offsets_buffer)
			blendshape_offsets_buffer = np.reshape(blendshape_offsets_buffer, (-1, 3))
			blendshape_offsets_buffer[:, [1, 2]] = blendshape_offsets_buffer[:, [2, 1]]
			blendshape_offsets_buffer[:, 2] *= -1
			blendshape_offsets_buffer -= buffer_vertices

			blendshape_normals_buffer = np.array(shape_key.normals_vertex_get(), dtype=determine_pack_format_float(float_width))
			blendshape_normals_buffer = np.reshape(blendshape_normals_buffer, (-1, 3))
			blendshape_normals_buffer[:, [1, 2]] = blendshape_normals_buffer[:, [2, 1]]
			blendshape_normals_buffer[:, 2] *= -1
			
			blendshape_offset_lengths = np.linalg.norm(blendshape_offsets_buffer, 1, 1)
			blendshape_offset_lengths_valid = np.where(blendshape_offset_lengths > 0.0001, True, False)
			num_valid = np.count_nonzero(blendshape_offset_lengths_valid)

			indexed = num_valid < len(blender_mesh.vertices) * 0.833

			blendshape = {
				"name": shape_key.name,
				"indexed": indexed,
				"count": num_valid if indexed else len(blender_mesh.vertices),
				"default_value": shape_key.value,
				"limit_upper": shape_key.slider_max,
				"limit_lower": shape_key.slider_min,
			}
			if(indexed):
				blendhshape_indices_buffer = np.extract(blendshape_offset_lengths_valid, np.arange(len(blender_mesh.vertices), dtype=determine_pack_format_uint(indices_width)))
				np.take(blendshape_offsets_buffer, blendhshape_indices_buffer, 0)
				blendshape["indices"] = context.serialize_buffer(blendhshape_indices_buffer.tobytes())
				blendshape["position_offsets"] = context.serialize_buffer(np.take(blendshape_offsets_buffer, blendhshape_indices_buffer, 0).tobytes())
				blendshape["normal_offsets"] = context.serialize_buffer(np.take(blendshape_normals_buffer, blendhshape_indices_buffer, 0).tobytes())
			else:
				blendshape["position_offsets"] = context.serialize_buffer(blendshape_offsets_buffer.tobytes())
				blendshape["normal_offsets"] = context.serialize_buffer(blendshape_normals_buffer.tobytes())
			blendshapes.append(blendshape)
		stf_mesh["blendshapes"] = blendshapes

	return stf_mesh, blender_mesh.stf_id
