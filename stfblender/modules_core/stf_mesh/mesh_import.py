from io import BytesIO
import bpy

from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.trs_utils import stf_translation_to_blender
from ...utils.buffer_utils import parse_float, parse_uint


_stf_type = "stf.mesh"


def import_stf_mesh(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
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


	# Construct the topology
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

	if("armature" in json_resource and "bones" in json_resource and "weights" in json_resource):
		armature: bpy.types.Armature = mesh_context.import_resource(json_resource["armature"])
		if(not armature):
			mesh_context.report(STFReport("Invalid Armature (armature id: " + json_resource["armature"] + " )", STFReportSeverity.Error, id, _stf_type, blender_mesh))
		else:
			blender_bone_mappings = {}
			bones = json_resource["bones"]
			for index, bone_id in bones.items():
				bone = None
				for blender_bone in armature.bones:
					if(blender_bone.stf_id == bone_id):
						bone = blender_bone
						break
				if(not bone):
					mesh_context.report(STFReport("Invalid Bone Mapping (bone_id: " + bone_id + " )", STFReportSeverity.Error, id, _stf_type, blender_mesh))
				else:
					blender_bone_mappings[index] = bone.name

			print(blender_bone_mappings)
			for weight_channel in json_resource["weights"]:
				print(weight_channel)



	return blender_mesh, mesh_context
