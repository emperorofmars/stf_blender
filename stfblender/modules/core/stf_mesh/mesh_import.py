from io import BytesIO
import bpy
import numpy as np

from ....importer.stf_import_context import STF_ImportContext
from ....core.stf_report import STFReportSeverity, STFReport
from ....utils.trs_utils import stf_translation_to_blender, stf_uv_to_blender
from ....core.buffer_utils import determine_pack_format_float, determine_pack_format_uint, parse_float, parse_int, parse_uint


_stf_type = "stf.mesh"


# Mesh import and export are the lowest hanging fruits for performance improvements.

def import_stf_mesh(context: STF_ImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_mesh = bpy.data.meshes.new(json_resource.get("name", "STF Mesh"))
	blender_mesh.stf_id = stf_id
	if(json_resource.get("name")):
		blender_mesh.stf_name = json_resource["name"]
		blender_mesh.stf_name_source_of_truth = True

	tmp_blender_mesh_object = bpy.data.objects.new("STF TMP throw away", blender_mesh)
	def _clean_tmp_mesh_object():
		bpy.data.objects.remove(tmp_blender_mesh_object)
	context.add_cleanup_task(_clean_tmp_mesh_object)

	indices_width: int = json_resource.get("indices_width", 4)
	float_width: int = json_resource.get("float_width", 4)


	# Vertices
	buffer_vertices = np.copy(np.frombuffer(context.import_buffer(json_resource["vertices"]), dtype=determine_pack_format_float(float_width)))
	buffer_vertices = np.reshape(buffer_vertices, (-1, 3))
	buffer_vertices[:, 2] *= -1
	buffer_vertices[:, [1, 2]] = buffer_vertices[:, [2, 1]]

	# Splits
	buffer_splits = np.frombuffer(context.import_buffer(json_resource["splits"]), dtype=determine_pack_format_uint(indices_width))

	# Faces
	py_faces = []
	if("faces" in json_resource and "tris" in json_resource):
		buffer_faces = BytesIO(context.import_buffer(json_resource["faces"]))
		buffer_tris = BytesIO(context.import_buffer(json_resource["tris"]))

		for index in range(int(buffer_faces.getbuffer().nbytes / indices_width)):
			face_len = parse_uint(buffer_faces, indices_width)
			face_splits = set()
			for _ in range(face_len):
				face_splits.add(parse_uint(buffer_tris, indices_width))
				face_splits.add(parse_uint(buffer_tris, indices_width))
				face_splits.add(parse_uint(buffer_tris, indices_width))

			face_indices = []
			for split_index in sorted(face_splits):
				face_indices.append(buffer_splits[split_index])
			py_faces.append(face_indices)


	# Lines (Edges not part of faces)
	py_lines = []
	if("lines" in json_resource):
		buffer_lines = BytesIO(context.import_buffer(json_resource["lines"]))
		for _line_index in range(int(buffer_lines.getbuffer().nbytes / indices_width)):
			py_lines.append([parse_uint(buffer_lines, indices_width), parse_uint(buffer_lines, indices_width)])


	# Construct the topology
	blender_mesh.from_pydata(buffer_vertices, py_lines, py_faces, False)
	if(blender_mesh.validate(verbose=True)): # return is True if errors found
		context.report(STFReport("Invalid mesh", STFReportSeverity.Error, stf_id, _stf_type, blender_mesh))


	# Face smooth setting
	if("sharp_face_indices" in json_resource):
		buffer_sharp_face_indices = BytesIO(context.import_buffer(json_resource["sharp_face_indices"]))
		for _ in range(int(buffer_sharp_face_indices.getbuffer().nbytes / indices_width)):
			smooth_index = parse_uint(buffer_sharp_face_indices, indices_width)
			blender_mesh.polygons[smooth_index].use_smooth = False

	# Explicit edge sharpness
	if("sharp_edges" in json_resource):
		buffer_sharp_edges = BytesIO(context.import_buffer(json_resource["sharp_edges"]))

		edge_dict: dict[int, dict[int, bpy.types.MeshEdge]] = {}
		for edge in blender_mesh.edges:
			if(edge.vertices[0] not in edge_dict):
				edge_dict[edge.vertices[0]] = {}
			edge_dict[edge.vertices[0]][edge.vertices[1]] = edge

		for line_index in range(int(buffer_sharp_edges.getbuffer().nbytes / (indices_width * 2))):
			v0_index = parse_uint(buffer_sharp_edges, indices_width)
			v1_index = parse_uint(buffer_sharp_edges, indices_width)
			if(v0_index in edge_dict and v1_index in edge_dict[v0_index]):
				edge_dict[v0_index][v1_index].use_edge_sharp = True
			elif(v1_index in edge_dict and v0_index in edge_dict[v1_index]):
				edge_dict[v1_index][v0_index].use_edge_sharp = True
			else:
				pass # TODO warn about invalid data

	if("colors" in json_resource):
		for index in range(len(json_resource["colors"])):
			color_attribute = blender_mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
			buffer_vertex_colors = BytesIO(context.import_buffer(json_resource["colors"][index]))
			for index, _vertex in enumerate(blender_mesh.vertices):
				r = parse_float(buffer_vertex_colors, float_width)
				g = parse_float(buffer_vertex_colors, float_width)
				b = parse_float(buffer_vertex_colors, float_width)
				a = parse_float(buffer_vertex_colors, float_width)
				color_attribute.data[index].color = (r, g, b, a)

	# Face corners (Splits)
	if("splits" in json_resource):
		if("split_normals" in json_resource):
			buffer_split_normals = np.copy(np.frombuffer(context.import_buffer(json_resource["split_normals"]), dtype=determine_pack_format_float(float_width)))
			buffer_split_normals = np.reshape(buffer_split_normals, (-1, 3))
			buffer_split_normals[:, 2] *= -1
			buffer_split_normals[:, [1, 2]] = buffer_split_normals[:, [2, 1]]
			blender_mesh.normals_split_custom_set(buffer_split_normals)

		if("uvs" in json_resource):
			for uv_layer_index in range(len(json_resource["uvs"])):
				uv_layer = blender_mesh.uv_layers.new(name=json_resource["uvs"][uv_layer_index].get("name", "UVMap"))
				buffer_uv = np.copy(np.frombuffer(context.import_buffer(json_resource["uvs"][uv_layer_index]["uv"]), dtype=determine_pack_format_float(float_width)))
				buffer_uv = np.reshape(buffer_uv, (-1, 2))
				buffer_uv[:, 1] = 1 - buffer_uv[:, 1]
				uv_layer.uv.foreach_set("vector", np.reshape(buffer_uv, -1))

		if("split_colors" in json_resource):
			for index in range(len(json_resource["split_colors"])):
				color_attribute = blender_mesh.color_attributes.new("Color", "FLOAT_COLOR", "POINT")
				buffer_split_colors = BytesIO(context.import_buffer(json_resource["split_colors"][index]))
				for index, vertex in enumerate(blender_mesh.vertices):
					r = parse_float(buffer_split_colors, float_width)
					g = parse_float(buffer_split_colors, float_width)
					b = parse_float(buffer_split_colors, float_width)
					a = parse_float(buffer_split_colors, float_width)
					color_attribute.data[index].color = (r, g, b, a)

	# Material slots and material slot indices
	if("material_slots" in json_resource):
		for material_slot in json_resource["material_slots"]:
			material = None
			if(material_slot):
				material = context.import_resource(material_slot, stf_kind="data")
			blender_mesh.materials.append(material)

	if("material_indices" in json_resource):
		material_indices_width = json_resource.get("material_indices_width", 4)
		buffer_material_indices = BytesIO(context.import_buffer(json_resource["material_indices"]))
		for polygon in blender_mesh.polygons:
			polygon.material_index = parse_uint(buffer_material_indices, material_indices_width)


	# Weight paint
	if("armature" in json_resource and "weights" in json_resource and "bones" in json_resource):
		armature: bpy.types.Armature = context.import_resource(json_resource["armature"], stf_kind="data")
		if(not armature):
			context.report(STFReport("Invalid Armature (armature id: " + json_resource["armature"] + " )", STFReportSeverity.Error, stf_id, _stf_type, blender_mesh))
		else:
			bone_indices_width = json_resource.get("bone_indices_width", 1)
			bones = []
			vertex_groups = []
			for bone_id in json_resource["bones"]:
				for blender_bone in armature.bones:
					if(blender_bone.stf_id == bone_id):
						bones.append(blender_bone.name)
						vertex_groups.append(tmp_blender_mesh_object.vertex_groups.new(name=blender_bone.name))
						break
			if(len(vertex_groups) < len(json_resource["bones"])):
				context.report(STFReport("Invalid Bone Mapping", STFReportSeverity.Error, stf_id, _stf_type, blender_mesh))
			
			buffer_weight_lens = BytesIO(context.import_buffer(json_resource["weight_lens"]))
			buffer_weights = BytesIO(context.import_buffer(json_resource["weights"]))
			for vertex in blender_mesh.vertices:
				weights_count = parse_uint(buffer_weight_lens, indices_width)
				for weight_index in range(weights_count):
					bone_index = parse_uint(buffer_weights, bone_indices_width)
					weight = parse_float(buffer_weights, float_width)
					if(weight > 0):
						vertex_groups[bone_index].add([vertex.index], weight, "REPLACE")

	# Vertex groups
	if("vertex_groups" in json_resource):
		for vertex_group_index, json_vertex_group in enumerate(json_resource["vertex_groups"]):
			indexed = json_vertex_group["indexed"]
			count = json_vertex_group["count"]
			buffer_vertex_weights = BytesIO(context.import_buffer(json_vertex_group["buffer"]))
			vertex_group = tmp_blender_mesh_object.vertex_groups.new(name=json_vertex_group.get("name", "STF Vertex Group " + str(vertex_group_index)))
			for index in range(count):
				## let vertex_index
				if(indexed):
					vertex_index = parse_uint(buffer_vertex_weights, indices_width)
				else:
					vertex_index = index
				weight = parse_float(buffer_vertex_weights, float_width)
				if(weight > 0):
					vertex_group.add([vertex_index], weight, "REPLACE")

	# Blendshapes / Morphtargets / Shapekeys / Blendtargets / Targetblends / Targetshapes / Morphshapes / Blendkeys / Shapetargets / Shapemorphs / Blendmorphs / Blendtargets / Morphblends / Morphkeys / Shapeblends / Blendblends / ...
	if("blendshapes" in json_resource):
		tmp_blender_mesh_object.shape_key_add(name="Basis", from_mix=False)
		for blendshape_index, json_blendshape in enumerate(json_resource["blendshapes"]):
			indexed = json_blendshape["indexed"]
			count = json_blendshape["count"]

			buffer_blendshape_pos_offset = np.copy(np.frombuffer(context.import_buffer(json_blendshape["position_offsets"]), dtype=determine_pack_format_float(float_width)))
			buffer_blendshape_pos_offset = np.reshape(buffer_blendshape_pos_offset, (-1, 3))
			buffer_blendshape_pos_offset[:, 2] *= -1
			buffer_blendshape_pos_offset[:, [1, 2]] = buffer_blendshape_pos_offset[:, [2, 1]]

			if(indexed):
				buffer_blendshape_indices = np.frombuffer(context.import_buffer(json_blendshape["indices"]), dtype=determine_pack_format_uint(indices_width))
				buffer_blendshape_pos_offset_indexed = buffer_blendshape_pos_offset
				buffer_blendshape_pos_offset = np.zeros((len(blender_mesh.vertices), 3), dtype=determine_pack_format_float(float_width))
				for index, vertex_index in enumerate(buffer_blendshape_indices):
					buffer_blendshape_pos_offset[vertex_index] = buffer_blendshape_pos_offset_indexed[index]

			# todo import vertices into numpy array and use that
			buffer_vertices = np.zeros(len(blender_mesh.vertices) * 3, dtype=determine_pack_format_float(float_width))
			blender_mesh.vertices.foreach_get("co", buffer_vertices)
			buffer_vertices = np.reshape(buffer_vertices, (-1, 3))

			buffer_blendshape_pos_offset += buffer_vertices

			# Normals and Tangents are irrelevant to import into Blender

			shape_key = tmp_blender_mesh_object.shape_key_add(name=json_blendshape.get("name", "STF Blendshape " + str(blendshape_index)), from_mix=False)

			shape_key.data.foreach_set("co", np.reshape(buffer_blendshape_pos_offset, -1))

			shape_key.value = json_blendshape.get("default_value", 0)
			shape_key.slider_max = json_blendshape.get("limit_upper", 1)
			shape_key.slider_min = json_blendshape.get("limit_lower", 0)

	return blender_mesh
