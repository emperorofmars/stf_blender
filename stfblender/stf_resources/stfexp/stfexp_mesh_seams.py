# pyright: reportIndexIssue=none

import bpy
import uuid
from io import BytesIO
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_ExportComponentHook, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.utils.buffer_utils import determine_indices_width, parse_uint, serialize_uint


_stf_type = "stfexp.mesh.seams"
_blender_property_name = "stfexp_mesh_seams"


class STFEXP_Mesh_Seams(STF_ComponentResourceBase):
	pass


class Handler_STF_Mesh_Seams(STF_Handler_Component):
	"""Represents the existence of mesh-seams. If they are present, Blender will automatically create this component on export, no need to add it manually"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [STFEXP_Mesh_Seams]

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Mesh | None) -> Any | STFReport:
		buffer_seams = BytesIO(context.import_buffer(json_resource, json_resource["seams"])) # pyright: ignore[reportArgumentType]

		indices_width: int = json_resource.get("indices_width", 4)

		edge_dict: dict[int, dict[int, bpy.types.MeshEdge]] = {}
		for edge in context_resource.edges:
			if(edge.vertices[0] not in edge_dict):
				edge_dict[edge.vertices[0]] = {}
			if(edge.vertices[1] not in edge_dict):
				edge_dict[edge.vertices[1]] = {}
			edge_dict[edge.vertices[0]][edge.vertices[1]] = edge
			edge_dict[edge.vertices[1]][edge.vertices[0]] = edge

		for _ in range(int((buffer_seams.getbuffer().nbytes / indices_width) / 2)):
			v0_index = parse_uint(buffer_seams, indices_width) # pyright: ignore[reportArgumentType]
			v1_index = parse_uint(buffer_seams, indices_width) # pyright: ignore[reportArgumentType]
			edge_dict[v0_index][v1_index].use_seam = True

		component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type)
		import_component_base(context, component, json_resource, _blender_property_name, context_resource)

		return component

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: STFEXP_Mesh_Seams, context_resource: bpy.types.Mesh | None) -> tuple[dict, str]:
		ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)

		indices_width = determine_indices_width(len(context_resource.loops))

		buffer_seams = BytesIO()
		for edge in context_resource.edges:
			if(edge.use_seam and not edge.is_loose):
				for edge_vertex_index in edge.vertices: # pyright: ignore[reportGeneralTypeIssues]
					buffer_seams.write(serialize_uint(edge_vertex_index, indices_width))
		ret["indices_width"] = indices_width
		ret["seams"] = context.serialize_buffer(ret, buffer_seams.getvalue())

		return ret, blender_resource.stf_id


class HOOK_STFEXP_Mesh_Seams(STF_ExportComponentHook):
	hook_understood_blender_types = [bpy.types.Mesh]

	@staticmethod
	def hook_can_handle_blender_resource(blender_resource: Any) -> bool:
		mesh: bpy.types.Mesh = blender_resource
		if(mesh.stfexp_mesh_seams and len(mesh.stfexp_mesh_seams) > 0): return False
		return True

	@staticmethod
	def hook_export_resource(context: STF_ExportContext, blender_resource: bpy.types.Mesh, context_resource: Any):
		add_component(blender_resource, _blender_property_name, str(uuid.uuid4()), _stf_type)


def register():
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Mesh_Seams, options=set()))

def unregister():
	if hasattr(bpy.types.Mesh, _blender_property_name):
		delattr(bpy.types.Mesh, _blender_property_name)
