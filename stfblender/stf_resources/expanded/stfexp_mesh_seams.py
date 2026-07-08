import bpy
import uuid
from io import BytesIO
from typing import Any

from ....stf_blender_common.blender_data.stf_resource_component import STF_ComponentResourceBase
from ....stf_blender_common.protocols import PSTF_ExportContext, PSTF_ImportContext, STF_Handler_Component, STF_ExportComponentHook
from ....stf_blender_common.base import STF_Category
from ....stf_blender_common.utils.component_resource_utils import add_component, export_component_base, import_component_base
from ....stf_blender_common.utils.buffer_utils import determine_indices_width, parse_uint, serialize_uint


_stf_type = "stfexp.mesh.seams"
_blender_property_name = "stfexp_mesh_seams"


class STFEXP_Mesh_Seams(STF_ComponentResourceBase):
	pass


def _stf_import(context: PSTF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Mesh) -> Any:
	buffer_seams = BytesIO(context.import_buffer(json_resource, json_resource["seams"])) # pyright: ignore[reportArgumentType]

	indices_width: int = json_resource.get("indices_width", 4)

	edge_dict: dict[int, dict[int, bpy.types.MeshEdge]] = {}
	for edge in context_object.edges:
		if(edge.vertices[0] not in edge_dict): # pyright: ignore[reportIndexIssue]
			edge_dict[edge.vertices[0]] = {} # pyright: ignore[reportIndexIssue]
		if(edge.vertices[1] not in edge_dict): # pyright: ignore[reportIndexIssue]
			edge_dict[edge.vertices[1]] = {} # pyright: ignore[reportIndexIssue]
		edge_dict[edge.vertices[0]][edge.vertices[1]] = edge # pyright: ignore[reportIndexIssue]
		edge_dict[edge.vertices[1]][edge.vertices[0]] = edge # pyright: ignore[reportIndexIssue]

	for _ in range(int((buffer_seams.getbuffer().nbytes / indices_width) / 2)):
		v0_index = parse_uint(buffer_seams, indices_width) # pyright: ignore[reportArgumentType]
		v1_index = parse_uint(buffer_seams, indices_width) # pyright: ignore[reportArgumentType]
		edge_dict[v0_index][v1_index].use_seam = True

	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	return component


def _stf_export(context: PSTF_ExportContext, component: STFEXP_Mesh_Seams, context_object: bpy.types.Mesh) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)

	indices_width = determine_indices_width(len(context_object.loops))

	buffer_seams = BytesIO()
	for edge in context_object.edges:
		if(edge.use_seam and not edge.is_loose):
			for edge_vertex_index in edge.vertices: # pyright: ignore[reportGeneralTypeIssues]
				buffer_seams.write(serialize_uint(edge_vertex_index, indices_width))
	ret["indices_width"] = indices_width
	ret["seams"] = context.serialize_buffer(ret, buffer_seams.getvalue())

	return ret, component.stf_id


class Handler_STF_Mesh_Seams(STF_Handler_Component):
	"""Represents the existence of mesh-seams. If they are present, Blender will automatically create this component on export, no need to add it manually"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	understood_application_types = [STFEXP_Mesh_Seams]
	import_func = _stf_import # pyright: ignore[reportAssignmentType]
	export_func = _stf_export # pyright: ignore[reportAssignmentType]

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]


def _hook_can_handle_func(application_object: Any) -> bool:
	mesh: bpy.types.Mesh = application_object
	if(mesh.stfexp_mesh_seams and len(mesh.stfexp_mesh_seams) > 0): return False
	return True

def _hook_apply_func(context: PSTF_ExportContext, application_object: bpy.types.Mesh, context_object: Any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_STFEXP_Mesh_Seams(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Mesh]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func


register_stf_handlers = [
	Handler_STF_Mesh_Seams,
	HOOK_STFEXP_Mesh_Seams
]


def register():
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Mesh_Seams, options=set()))

def unregister():
	if hasattr(bpy.types.Mesh, _blender_property_name):
		delattr(bpy.types.Mesh, _blender_property_name)
