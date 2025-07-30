from io import BytesIO
import bpy
import numpy as np
import mathutils

from ....exporter.stf_export_context import STF_ExportContext
from ....utils.id_utils import ensure_stf_id
from ....core.buffer_utils import determine_indices_width, determine_pack_format_float, determine_pack_format_uint, serialize_float, serialize_uint


_stf_type = "stf.mesh"


default_export_options: dict = {
	"export_normals": True,
	"export_colors": True,
	"export_blendshape_normals": True,
	"float_treshhold": 0.0001,
	"float_treshhold_blendshape": 0.0001,
}


# Mesh import and export are the lowest hanging fruits for performance improvements.

def export_stf_mesh(context: STF_ExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str]:
	export_options = dict(default_export_options)
	export_options["export_colors"] = context.get_setting("stf_mesh_vertex_colors", export_options["export_colors"])
	export_options["export_blendshape_normals"] = context.get_setting("stf_mesh_blendshape_normals", export_options["export_blendshape_normals"])

	blender_mesh: bpy.types.Mesh = application_object
	ensure_stf_id(context, blender_mesh)

	armature: bpy.types.Armature = parent_application_object

	tmp_blender_mesh_object: bpy.types.Object = bpy.data.objects.new("TRASH", blender_mesh)
	context.register_trash_object(tmp_blender_mesh_object)
	bpy.context.scene.collection.objects.link(tmp_blender_mesh_object)

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

	indices_width = determine_indices_width(len(blender_mesh.loops))

	stf_mesh["float_width"] = float_width
	stf_mesh["indices_width"] = indices_width

	# Vertex positions
	buffer_vertices = np.zeros(len(blender_mesh.vertices) * 3, dtype=determine_pack_format_float(float_width))
	blender_mesh.vertices.foreach_get("co", buffer_vertices)
	buffer_vertices = np.reshape(buffer_vertices, (-1, 3))
	buffer_vertices[:, [1, 2]] = buffer_vertices[:, [2, 1]]
	buffer_vertices[:, 2] *= -1
	stf_mesh["vertices"] = context.serialize_buffer(buffer_vertices.tobytes())

	# Prepare optimization of splits
	def compareUVs(a: int, b: int) -> bool:
		for uv_layer in blender_mesh.uv_layers:
			if ((uv_layer.uv[a].vector - uv_layer.uv[b].vector).length > export_options["float_treshhold"]):
				return False
		return True
	
	def compareColors(a: int, b: int) -> bool:
		if(not export_options["export_colors"] or not blender_mesh.color_attributes.active_color or blender_mesh.color_attributes.active_color.domain != "CORNER"): return True
		return (mathutils.Vector(blender_mesh.color_attributes.active_color.data[a].color[:]) - mathutils.Vector(blender_mesh.color_attributes.active_color.data[b].color[:])).length < export_options["float_treshhold"]

	verts_to_split: dict[int, list] = {}
	deduped_split_indices: list[int] = []
	face_corners_to_split: list[int] = []
	for loop in blender_mesh.loops:
		if (loop.vertex_index not in verts_to_split):
			verts_to_split[loop.vertex_index] = [loop.index]
			deduped_split_indices.append(loop.index)
			face_corners_to_split.append(len(deduped_split_indices) - 1)
		else:
			for candidate_index in range(len(verts_to_split[loop.vertex_index])):
				split_candidate = verts_to_split[loop.vertex_index][candidate_index]
				if (
					(loop.normal - blender_mesh.loops[split_candidate].normal).length < export_options["float_treshhold"]
					and compareUVs(loop.index, split_candidate)
					and compareColors(loop.index, split_candidate)
				):
					face_corners_to_split.append(face_corners_to_split[split_candidate])
					break
			else:
				verts_to_split[loop.vertex_index].append(loop.index)
				deduped_split_indices.append(loop.index)
				face_corners_to_split.append(len(deduped_split_indices) - 1)
	
	deduped_split_indices = np.array(deduped_split_indices, dtype=determine_pack_format_uint(indices_width))
	face_corners_to_split = np.array(face_corners_to_split, dtype=determine_pack_format_uint(indices_width))


	# Splits & face corners
	buffer_splits = np.zeros(len(blender_mesh.loops), dtype=determine_pack_format_uint(indices_width))
	blender_mesh.loops.foreach_get("vertex_index", buffer_splits)
	buffer_splits = buffer_splits[deduped_split_indices]
	
	stf_mesh["face_corners"] = context.serialize_buffer(face_corners_to_split.tobytes()) # Index of unique face corners to index of shared split data
	stf_mesh["splits"] = context.serialize_buffer(buffer_splits.tobytes())

	# Split normals
	buffer_split_normals = np.zeros(len(blender_mesh.loops) * 3, dtype=determine_pack_format_float(float_width))
	blender_mesh.loops.foreach_get("normal", buffer_split_normals)
	buffer_split_normals = np.reshape(buffer_split_normals, (-1, 3))
	buffer_split_normals = buffer_split_normals[deduped_split_indices]
	buffer_split_normals[:, [1, 2]] = buffer_split_normals[:, [2, 1]]
	buffer_split_normals[:, 2] *= -1
	stf_mesh["split_normals"] = context.serialize_buffer(buffer_split_normals.tobytes())

	# Uvs
	uvs = []
	for uv_index, uv_layer in enumerate(blender_mesh.uv_layers):
		buffer_uv = np.zeros(len(blender_mesh.loops) * 2, dtype=determine_pack_format_float(float_width))
		uv_layer.uv.foreach_get("vector", buffer_uv)
		buffer_uv = np.reshape(buffer_uv, (-1, 2))
		buffer_uv = buffer_uv[deduped_split_indices]
		buffer_uv[:, 1] = 1 - buffer_uv[:, 1]
		uvs.append({"name": uv_layer.name, "uv": context.serialize_buffer(buffer_uv.tobytes())})
	stf_mesh["uvs"] = uvs

	# Split colors
	if(export_options["export_colors"] and blender_mesh.color_attributes.active_color):
		if(blender_mesh.color_attributes.active_color.domain == "CORNER"):
			color_buffer = np.zeros(len(blender_mesh.loops) * 4, dtype=determine_pack_format_float(float_width))
			blender_mesh.color_attributes.active_color.data.foreach_get("color", color_buffer)
			color_buffer = np.reshape(color_buffer, (-1, 4))
			color_buffer = color_buffer[deduped_split_indices]
			stf_mesh["split_colors"] = context.serialize_buffer(color_buffer.tobytes())


	# Topology
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
	material_indices_width = determine_indices_width(len(blender_mesh.materials))
	stf_mesh["material_indices_width"] = material_indices_width
	buffer_faces = BytesIO()
	buffer_face_material_indices = BytesIO()
	buffer_flat_face_indices = BytesIO()
	for polygon in blender_mesh.polygons:
		buffer_faces.write(serialize_uint(face_lens[polygon.index], indices_width))
		buffer_face_material_indices.write(serialize_uint(polygon.material_index, material_indices_width))
		if(not polygon.use_smooth):
			buffer_flat_face_indices.write(serialize_uint(polygon.index, indices_width))

	stf_mesh["faces"] = context.serialize_buffer(buffer_faces.getvalue())
	stf_mesh["material_indices"] = context.serialize_buffer(buffer_face_material_indices.getvalue())
	stf_mesh["sharp_face_indices"] = context.serialize_buffer(buffer_flat_face_indices.getvalue())

	# Lines (Edges not part of any face)
	buffer_lines = BytesIO()
	for edge in blender_mesh.edges:
		if(edge.is_loose):
			for edge_vertex_index in edge.vertices:
				buffer_lines.write(serialize_uint(edge_vertex_index, indices_width))
	stf_mesh["lines"] = context.serialize_buffer(buffer_lines.getvalue())

	# Explicit edge sharpness
	buffer_sharp_edges = BytesIO()
	for edge in blender_mesh.edges:
		if(edge.use_edge_sharp and not edge.is_loose):
			for edge_vertex_index in edge.vertices:
				buffer_sharp_edges.write(serialize_uint(edge_vertex_index, indices_width))
	stf_mesh["sharp_edges"] = context.serialize_buffer(buffer_sharp_edges.getvalue())

	# TODO explicit vertex sharpness at some point Blender plz


	# Weightpaint
	if(armature and tmp_blender_mesh_object):
		stf_mesh["armature"] = context.serialize_resource(armature)

		# Create vertex group lookup dictionary for stf_ids
		weight_bone_map = []
		# dict[blendergroup_index, bone_id_index]
		group_to_bone_index: dict[int, int] = {}
		for group in tmp_blender_mesh_object.vertex_groups:
			if(group.name in armature.bones):
				weight_bone_map.append(armature.bones[group.name].stf_id)
				group_to_bone_index[group.index] = len(weight_bone_map) - 1
		stf_mesh["bones"] = weight_bone_map

		bone_indices_width = determine_indices_width(len(weight_bone_map))
		stf_mesh["bone_indices_width"] = bone_indices_width

		max_len_weights_per_vertex = 0

		# list[list[tuple[bone_index, weight]]]
		vertex_weights: list[list[tuple[int, float]]] = []
		for vertex in blender_mesh.vertices:
			group_arr = []
			for channel, group in enumerate(vertex.groups):
				if(group.group in group_to_bone_index and group.weight > export_options["float_treshhold_blendshape"]):
					group_arr.append((group_to_bone_index[group.group], group.weight))
			group_arr.sort(key=lambda e: e[1], reverse=True)
			max_len_weights_per_vertex = max(max_len_weights_per_vertex, len(group_arr))
			vertex_weights.append(group_arr)

		weight_lens_width = determine_indices_width(max_len_weights_per_vertex)
		
		stf_mesh["weight_lens_width"] = weight_lens_width

		weight_lens = BytesIO()
		buffer_bone_indices = BytesIO()
		buffer_weights = BytesIO()
		for weights in vertex_weights:
			# Write the number of weights for that vertex
			weight_lens.write(serialize_uint(len(weights), weight_lens_width)) # weights per vertex
			for weight in weights:
				# Write the bone index and bone weight
				buffer_bone_indices.write(serialize_uint(weight[0], bone_indices_width)) # bone index
				buffer_weights.write(serialize_float(weight[1], float_width)) # bone weight

		stf_mesh["weight_lens"] = context.serialize_buffer(weight_lens.getvalue())
		stf_mesh["bone_indices"] = context.serialize_buffer(buffer_bone_indices.getvalue())
		stf_mesh["weights"] = context.serialize_buffer(buffer_weights.getvalue())


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
				buffer_indices = BytesIO()
				buffer_weights = BytesIO()
				if(indexed):
					for vertex_index, weight in group.items():
						buffer_indices.write(serialize_uint(vertex_index, indices_width)) # vertex index
						buffer_weights.write(serialize_float(weight, float_width)) # vertex weight
				else:
					for vertex in blender_mesh.vertices:
						if(vertex.index in group):
							buffer_weights.write(serialize_float(group[vertex.index], float_width)) # vertex weight
						else:
							buffer_weights.write(serialize_float(0, float_width)) # vertex weight
				vertex_group = {
					"name": vertex_group_name,
					"weights": context.serialize_buffer(buffer_weights.getvalue()),
				}
				if(indexed):
					vertex_group["indices"] = context.serialize_buffer(buffer_indices.getvalue())
				buffers_vertex_groups.append(vertex_group)
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

			blendshape_offset_lengths = np.linalg.norm(blendshape_offsets_buffer, 1, 1)
			blendshape_offset_lengths_valid = np.where(blendshape_offset_lengths > export_options["float_treshhold_blendshape"], True, False)
			num_valid = np.count_nonzero(blendshape_offset_lengths_valid)
			indexed = num_valid < len(blender_mesh.vertices) * 0.75
			# let blendhshape_indices_buffer
			if(indexed):
				blendhshape_indices_buffer = np.extract(blendshape_offset_lengths_valid, np.arange(len(blender_mesh.vertices), dtype=determine_pack_format_uint(indices_width)))

			# let blendshape_normals_split_buffer
			# let blendhshape_split_indices_buffer
			if(export_options["export_blendshape_normals"]):
				blendshape_normals_split_buffer = np.array(shape_key.normals_split_get(), dtype=determine_pack_format_float(float_width))
				blendshape_normals_split_buffer = np.reshape(blendshape_normals_split_buffer, (-1, 3))
				blendshape_normals_split_buffer = blendshape_normals_split_buffer[deduped_split_indices]
				blendshape_normals_split_buffer[:, [1, 2]] = blendshape_normals_split_buffer[:, [2, 1]]
				blendshape_normals_split_buffer[:, 2] *= -1

				if(indexed):
					valid_split_positions = blendshape_offset_lengths_valid[buffer_splits]
					blendhshape_split_indices_buffer = np.extract(valid_split_positions, np.arange(len(blender_mesh.loops), dtype=determine_pack_format_uint(indices_width)))

			blendshape = {
				"name": shape_key.name,
				"default_value": shape_key.value,
				"limit_upper": shape_key.slider_max,
				"limit_lower": shape_key.slider_min,
			}
			if(indexed):
				blendshape["indices"] = context.serialize_buffer(blendhshape_indices_buffer.tobytes())
				blendshape["position_offsets"] = context.serialize_buffer(np.take(blendshape_offsets_buffer, blendhshape_indices_buffer, 0).tobytes())
				if(export_options["export_blendshape_normals"]):
					blendshape["split_indices"] = context.serialize_buffer(blendhshape_split_indices_buffer.tobytes())
					blendshape["split_normals"] = context.serialize_buffer(np.take(blendshape_normals_split_buffer, blendhshape_split_indices_buffer, 0).tobytes())
			else:
				blendshape["position_offsets"] = context.serialize_buffer(blendshape_offsets_buffer.tobytes())
				if(export_options["export_blendshape_normals"]):
					blendshape["split_normals"] = context.serialize_buffer(blendshape_normals_split_buffer.tobytes())
			blendshapes.append(blendshape)
		stf_mesh["blendshapes"] = blendshapes

	return stf_mesh, blender_mesh.stf_id
