from io import BytesIO
import bpy

from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.trs_utils import stf_translation_to_blender, stf_uv_to_blender
from ...utils.buffer_utils import parse_float, parse_int, parse_uint


_stf_type = "stf.mesh"


def import_stf_mesh(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_mesh = bpy.data.meshes.new(json_resource.get("name", "STF Mesh"))
	blender_mesh.stf_id = id
	blender_mesh.stf_name = json_resource.get("name", "STF Mesh")

	blender_object_tmp = bpy.data.objects.new("STF TMP throw away", blender_mesh)
	def _clean_tmp_mesh_object():
		bpy.data.objects.remove(blender_object_tmp)
	context.add_task(_clean_tmp_mesh_object)

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
		face_indices_width = json_resource.get("face_indices_width", 4)
		buffer_faces = BytesIO(mesh_context.import_buffer(json_resource["faces"]))
		buffer_tris = BytesIO(mesh_context.import_buffer(json_resource["tris"]))

		for index in range(face_count):
			face_len = parse_uint(buffer_faces, face_indices_width)
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


	# Construct the topology
	blender_mesh.from_pydata(py_vertices, [], py_faces, False)
	if(blender_mesh.validate(verbose=True)): # return is True if errors found
		context.report(STFReport("Invalid mesh", STFReportSeverity.Error, id, _stf_type, blender_mesh))


	# Face smooth setting
	if("flat_face_indices" in json_resource and "flat_face_indices_len" in json_resource):
		flat_face_indices_len = json_resource["flat_face_indices_len"]
		face_indices_width = json_resource.get("face_indices_width", 4)
		buffer_flat_face_indices = BytesIO(mesh_context.import_buffer(json_resource["flat_face_indices"]))
		for _ in range(flat_face_indices_len):
			smooth_index = parse_uint(buffer_flat_face_indices, face_indices_width)
			blender_mesh.polygons[smooth_index].use_smooth = False

	"""# Vertex Normals
	if("normals" in json_resource):
		vertex_normals_width = json_resource.get("vertex_normals_width", 4)
		buffer_vertex_normals = BytesIO(mesh_context.import_buffer(json_resource["normals"]))
		for index, vertex in enumerate(blender_mesh.vertices):
			p0 = parse_float(buffer_vertex_normals, vertex_normals_width)
			p1 = parse_float(buffer_vertex_normals, vertex_normals_width)
			p2 = parse_float(buffer_vertex_normals, vertex_normals_width)
			vertex.normal = stf_translation_to_blender([p0, p1, p2])"""

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

	# Face corners (Splits)
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
					uv = stf_uv_to_blender([parse_float(buffer_uv, split_uv_width), parse_float(buffer_uv, split_uv_width)])
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

	# Material slots and material slot indices
	if("material_slots" in json_resource):
		for material_slot in json_resource["material_slots"]:
			material = None
			if(material_slot):
				material = mesh_context.import_resource(material_slot)
			blender_mesh.materials.append(material)

	material_indices_count = face_count if face_count > 0 else tris_count
	if("material_indices" in json_resource and material_indices_count > 0):
		material_indices_width = json_resource.get("material_indices_width", 4)
		buffer_material_indices = BytesIO(mesh_context.import_buffer(json_resource["material_indices"]))
		for polygon in blender_mesh.polygons:
			polygon.material_index = parse_uint(buffer_material_indices, material_indices_width)


	# Weight paint
	if("armature" in json_resource and "weights" in json_resource and "bones" in json_resource):
		armature: bpy.types.Armature = mesh_context.import_resource(json_resource["armature"])
		if(not armature):
			mesh_context.report(STFReport("Invalid Armature (armature id: " + json_resource["armature"] + " )", STFReportSeverity.Error, id, _stf_type, blender_mesh))
		else:
			bone_weight_width = json_resource.get("bone_weight_width", 4)
			bones = []
			vertex_groups = []
			for bone_id in json_resource["bones"]:
				for blender_bone in armature.bones:
					if(blender_bone.stf_id == bone_id):
						bones.append(blender_bone.name)
						vertex_groups.append(blender_object_tmp.vertex_groups.new(name=blender_bone.name))
						break
			if(len(vertex_groups) < len(json_resource["bones"])):
				mesh_context.report(STFReport("Invalid Bone Mapping", STFReportSeverity.Error, id, _stf_type, blender_mesh))

			for weight_channel in json_resource["weights"]:
				indexed = weight_channel["indexed"]
				weights_count = weight_channel["count"]
				buffer = BytesIO(mesh_context.import_buffer(weight_channel["buffer"]))

				for index in range(weights_count):
					if(indexed):
						vertex_index = parse_uint(buffer, vertex_indices_width)
					else:
						vertex_index = index
					bone_index = parse_int(buffer, vertex_indices_width)
					weight = parse_float(buffer, bone_weight_width)
					if(weight > 0 and bone_index >= 0):
						vertex_groups[bone_index].add([vertex_index], weight, "REPLACE")

	# Vertex groups
	if("vertex_groups" in json_resource):
		vertex_weight_width = json_resource.get("vertex_weight_width", 4)
		for vertex_group_index, json_vertex_group in enumerate(json_resource["vertex_groups"]):
			indexed = json_vertex_group["indexed"]
			count = json_vertex_group["count"]
			buffer_vertex_weights = BytesIO(mesh_context.import_buffer(json_vertex_group["buffer"]))
			vertex_group = blender_object_tmp.vertex_groups.new(name=json_vertex_group.get("name", "STF Vertex Group " + str(vertex_group_index)))
			for index in range(count):
				if(indexed):
					vertex_index = parse_uint(buffer_vertex_weights, vertex_indices_width)
				else:
					vertex_index = index
				weight = parse_float(buffer_vertex_weights, vertex_weight_width)
				if(weight > 0):
					vertex_group.add([vertex_index], weight, "REPLACE")

	# Blendshapes | Morphtargets | Shapekeys
	if("blendshapes" in json_resource):
		blendshape_pos_width = json_resource.get("blendshape_pos_width", 4)
		blender_object_tmp.shape_key_add(name="Basis", from_mix=False)
		for blendshape_index, json_blendshape in enumerate(json_resource["blendshapes"]):
			indexed = json_blendshape["indexed"]
			count = json_blendshape["count"]
			if(indexed):
				buffer_blendshape_indices = BytesIO(mesh_context.import_buffer(json_blendshape["indices"]))
			buffer_blendshape_pos_offset = BytesIO(mesh_context.import_buffer(json_blendshape["position_offsets"]))
			# Normals and Tangents are irrelevant to import into Blender

			shape_key = blender_object_tmp.shape_key_add(name=json_blendshape.get("name", "STF Blendshape " + str(blendshape_index)), from_mix=False)

			for index in range(count):
				if(indexed):
					vertex_index = parse_uint(buffer_blendshape_indices, vertex_indices_width)
				else:
					vertex_index = index
				pos_x = parse_float(buffer_blendshape_pos_offset, blendshape_pos_width)
				pos_y = parse_float(buffer_blendshape_pos_offset, blendshape_pos_width)
				pos_z = parse_float(buffer_blendshape_pos_offset, blendshape_pos_width)
				shape_key.data[vertex_index].co = blender_mesh.vertices[vertex_index].co + stf_translation_to_blender([pos_x, pos_y, pos_z])

	return blender_mesh, mesh_context
