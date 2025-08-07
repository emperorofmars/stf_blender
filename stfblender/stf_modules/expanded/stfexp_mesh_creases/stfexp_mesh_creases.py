from io import BytesIO
import uuid
import bpy
import numpy as np

from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component, export_component_base, import_component_base
from ....base.stf_module import STF_ExportComponentHook
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.buffer_utils import determine_indices_width, determine_pack_format_float
from ....utils.reference_helper import export_buffer


_stf_type = "stfexp.mesh.creases"
_blender_property_name = "stfexp_mesh_creases"


class STFEXP_Mesh_Creases(STF_BlenderComponentBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Mesh) -> any:
	buffer_edge_creases = BytesIO(context.import_buffer(json_resource["edge_creases"]))

	if("vertex_creases" in json_resource):
		buffer_vertex_creases = np.frombuffer(context.import_buffer(json_resource["vertex_creases"]), dtype=determine_pack_format_float(4))
		vertex_creases_attribute = context_object.attributes.new("crease_vert", "FLOAT", "POINT")
		vertex_creases_attribute.data.foreach_set("value", buffer_vertex_creases)
	
	if("edge_creases" in json_resource):
		indices_width: int = json_resource.get("indices_width", 4)
		buffer_edge_creases = np.frombuffer(context.import_buffer(json_resource["edge_creases"]), dtype=determine_pack_format_float(4))
		buffer_edges = np.frombuffer(context.import_buffer(json_resource["edges"]), dtype=determine_pack_format_float(indices_width))
		buffer_edges = np.reshape(buffer_edges, (-1, 2))

		edge_dict: dict[int, dict[int, int]] = {}
		for edge in context_object.edges:
			if(edge.vertices[0] not in edge_dict):
				edge_dict[edge.vertices[0]] = {}
			if(edge.vertices[1] not in edge_dict):
				edge_dict[edge.vertices[1]] = {}
			edge_dict[edge.vertices[0]][edge.vertices[1]] = edge.index
			edge_dict[edge.vertices[1]][edge.vertices[0]] = edge.index

		edge_creases_attribute = context_object.attributes.new("crease_edge", "FLOAT", "EDGE")

		for edge_index in range(len(buffer_edges)):
			v0_index = buffer_edges[edge_index][0]
			v1_index = buffer_edges[edge_index][1]
			edge_creases_attribute.data[edge_dict[v0_index][v1_index]].value = buffer_edge_creases[edge_index]

	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)

	return component


def _stf_export(context: STF_ExportContext, application_object: STFEXP_Mesh_Creases, context_object: bpy.types.Mesh) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)

	indices_width = determine_indices_width(len(context_object.loops))

	if(context_object.vertex_creases):
		buffer_vertex_creases = np.zeros(len(context_object.vertex_creases.data), dtype=determine_pack_format_float(4))
		context_object.vertex_creases.data.foreach_get("value", buffer_vertex_creases)
		ret["vertex_creases"] = export_buffer(ret, context.serialize_buffer(buffer_vertex_creases.tobytes()))

	if(context_object.edge_creases):
		buffer_edge_creases = np.zeros(len(context_object.edge_creases.data), dtype=determine_pack_format_float(4))
		context_object.edge_creases.data.foreach_get("value", buffer_edge_creases)
		ret["edge_creases"] = export_buffer(ret, context.serialize_buffer(buffer_edge_creases.tobytes()))

		buffer_edges = np.array(context_object.edge_keys, dtype=determine_pack_format_float(indices_width))
		ret["edges"] = export_buffer(ret, context.serialize_buffer(buffer_edges.tobytes()))
		ret["indices_width"] = indices_width

	return ret, application_object.stf_id


class STF_Module_STF_Mesh_Creases(STF_BlenderComponentModule):
	"""Represents the existence of mesh-creases. If they are present, Blender will automatically create this component on export, no need to add it manually"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [STFEXP_Mesh_Creases]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]



def _hook_can_handle_func(application_object: any) -> bool:
	mesh: bpy.types.Mesh = application_object
	if(not mesh.vertex_creases and not mesh.edge_creases): return False
	if(mesh.stfexp_mesh_creases and len(mesh.stfexp_mesh_creases) > 0): return False
	return True


def _hook_apply_func(context: STF_ExportContext, application_object: bpy.types.Mesh, context_object: any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_STFEXP_Mesh_Creases(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Mesh]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func



register_stf_modules = [
	STF_Module_STF_Mesh_Creases,
	HOOK_STFEXP_Mesh_Creases
]


def register():
	bpy.types.Mesh.stfexp_mesh_creases = bpy.props.CollectionProperty(type=STFEXP_Mesh_Creases) # type: ignore

def unregister():
	if hasattr(bpy.types.Mesh, "stfexp_mesh_creases"):
		del bpy.types.Mesh.stfexp_mesh_creases
