from io import BytesIO
import uuid
import bpy

from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component
from ....core.stf_module import STF_ExportComponentHook
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....core.buffer_utils import parse_uint, serialize_uint


_stf_type = "stfexp.mesh.seams"
_blender_property_name = "stfexp_mesh_seams"


class STFEXP_Mesh_Seams(STF_BlenderComponentBase):
	pass



def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Mesh) -> any:
	buffer_seams = BytesIO(context.import_buffer(json_resource["seams"]))

	vertex_indices_width = 4 if len(context_object.vertices) * 3 < 2**32 else 8

	edge_dict: dict[int, dict[int, bpy.types.MeshEdge]] = {}
	for edge in context_object.edges:
		if(edge.vertices[0] not in edge_dict):
			edge_dict[edge.vertices[0]] = {}
		edge_dict[edge.vertices[0]][edge.vertices[1]] = edge

	for seam_index in range(json_resource["seams_len"]):
		v0_index = parse_uint(buffer_seams, vertex_indices_width)
		v1_index = parse_uint(buffer_seams, vertex_indices_width)
		if(v0_index in edge_dict and v1_index in edge_dict[v0_index]):
			edge_dict[v0_index][v1_index].use_seam = True
		elif(v1_index in edge_dict and v0_index in edge_dict[v1_index]):
			edge_dict[v1_index][v0_index].use_seam = True
		else:
			pass # TODO warn about invalid data

	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)

	return component


def _stf_export(context: STF_ExportContext, application_object: STFEXP_Mesh_Seams, context_object: bpy.types.Mesh) -> tuple[dict, str]:
	ret = {
		"type": _stf_type
	}
	vertex_indices_width = 4 if len(context_object.vertices) * 3 < 2**32 else 8

	buffer_seams = BytesIO()
	seams_len = 0
	for edge in context_object.edges:
		if(edge.use_seam and not edge.is_loose):
			seams_len += 1
			for edge_vertex_index in edge.vertices:
				buffer_seams.write(serialize_uint(edge_vertex_index, vertex_indices_width))
	ret["seams_len"] = seams_len
	ret["seams"] = context.serialize_buffer(buffer_seams.getvalue())

	return ret, application_object.stf_id


class STF_Module_STF_Mesh_Seams(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [STFEXP_Mesh_Seams]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]



def _hook_can_handle_func(application_object: any) -> bool:
	mesh: bpy.types.Mesh = application_object
	if(mesh.stfexp_mesh_seams and len(mesh.stfexp_mesh_seams) > 0): return False
	return True


def _hook_apply_func(context: STF_ExportContext, application_object: bpy.types.Mesh, context_object: any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_STFEXP_Mesh_Seams(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Mesh]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func



register_stf_modules = [
	STF_Module_STF_Mesh_Seams,
	HOOK_STFEXP_Mesh_Seams
]


def register():
	bpy.types.Mesh.stfexp_mesh_seams = bpy.props.CollectionProperty(type=STFEXP_Mesh_Seams) # type: ignore

def unregister():
	if hasattr(bpy.types.Mesh, "stfexp_mesh_seams"):
		del bpy.types.Mesh.stfexp_mesh_seams
