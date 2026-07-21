# pyright: reportIndexIssue=none

import bpy
import uuid
from io import BytesIO
from typing import Any
import numpy as np

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_ExportComponentHook, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.utils.buffer_utils import determine_indices_width, determine_pack_format_float


_stf_type = "stfexp.mesh.creases"
_blender_property_name = "stfexp_mesh_creases"


class STFEXP_Mesh_Creases(STF_ComponentResourceBase):
	pass


class Handler_STF_Mesh_Creases(STF_Handler_Component):
	"""Represents the existence of mesh-creases. If they are present, Blender will automatically create this component on export, no need to add it manually"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [STFEXP_Mesh_Creases]

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Mesh | None) -> Any | STFReport:
		buffer_edge_creases = BytesIO(context.import_buffer(json_resource, json_resource["edge_creases"]))  # pyright: ignore[reportArgumentType]

		if("vertex_creases" in json_resource):
			buffer_vertex_creases = np.frombuffer(context.import_buffer(json_resource, json_resource["vertex_creases"]), dtype=determine_pack_format_float(4))  # pyright: ignore[reportCallIssue, reportArgumentType]
			vertex_creases_attribute = context_resource.attributes.new("crease_vert", "FLOAT", "POINT")
			vertex_creases_attribute.data.foreach_set("value", buffer_vertex_creases)

		if("edge_creases" in json_resource):
			indices_width: int = json_resource.get("indices_width", 4)
			buffer_edge_creases = np.frombuffer(context.import_buffer(json_resource, json_resource["edge_creases"]), dtype=determine_pack_format_float(4))  # pyright: ignore[reportCallIssue, reportArgumentType]
			buffer_edges = np.frombuffer(context.import_buffer(json_resource, json_resource["edges"]), dtype=determine_pack_format_float(indices_width))  # pyright: ignore[reportCallIssue, reportArgumentType]
			buffer_edges = np.reshape(buffer_edges, (-1, 2))

			edge_dict: dict[int, dict[int, int]] = {}
			for edge in context_resource.edges:
				if(edge.vertices[0] not in edge_dict):
					edge_dict[edge.vertices[0]] = {}
				if(edge.vertices[1] not in edge_dict):
					edge_dict[edge.vertices[1]] = {}
				edge_dict[edge.vertices[0]][edge.vertices[1]] = edge.index
				edge_dict[edge.vertices[1]][edge.vertices[0]] = edge.index

			edge_creases_attribute = context_resource.attributes.new("crease_edge", "FLOAT", "EDGE")

			for edge_index in range(len(buffer_edges)):
				v0_index = buffer_edges[edge_index][0]
				v1_index = buffer_edges[edge_index][1]
				edge_creases_attribute.data[edge_dict[v0_index][v1_index]].value = buffer_edge_creases[edge_index]

		component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type)
		import_component_base(context, component, json_resource, _blender_property_name, context_resource)

		return component

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: STFEXP_Mesh_Creases, context_resource: bpy.types.Mesh | None) -> tuple[dict, str]:
		ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)

		indices_width = determine_indices_width(len(context_resource.loops))

		if(context_resource.vertex_creases):
			buffer_vertex_creases = np.zeros(len(context_resource.vertex_creases.data), dtype=determine_pack_format_float(4))
			context_resource.vertex_creases.data.foreach_get("value", buffer_vertex_creases)
			ret["vertex_creases"] = context.serialize_buffer(ret, buffer_vertex_creases.tobytes())

		if(context_resource.edge_creases):
			buffer_edge_creases = np.zeros(len(context_resource.edge_creases.data), dtype=determine_pack_format_float(4))
			context_resource.edge_creases.data.foreach_get("value", buffer_edge_creases)
			ret["edge_creases"] = context.serialize_buffer(ret, buffer_edge_creases.tobytes())

			buffer_edges = np.array(context_resource.edge_keys, dtype=determine_pack_format_float(indices_width))
			ret["edges"] = context.serialize_buffer(ret, buffer_edges.tobytes())
			ret["indices_width"] = indices_width

		return ret, blender_resource.stf_id


class HOOK_STFEXP_Mesh_Creases(STF_ExportComponentHook):
	hook_understood_blender_types = [bpy.types.Mesh]

	@staticmethod
	def hook_can_handle_blender_resource(blender_resource: Any) -> bool:
		mesh: bpy.types.Mesh = blender_resource
		if(not mesh.vertex_creases and not mesh.edge_creases): return False
		if(mesh.stfexp_mesh_creases and len(mesh.stfexp_mesh_creases) > 0): return False
		return True

	@staticmethod
	def hook_export_resource(context: STF_ExportContext, blender_resource: bpy.types.Mesh, context_resource: Any):
		add_component(blender_resource, _blender_property_name, str(uuid.uuid4()), _stf_type)


def register():
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Mesh_Creases, options=set()))

def unregister():
	if hasattr(bpy.types.Mesh, _blender_property_name):
		delattr(bpy.types.Mesh, _blender_property_name)
