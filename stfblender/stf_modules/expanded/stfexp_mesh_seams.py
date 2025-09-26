from io import BytesIO
import uuid
import bpy

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_ExportComponentHook
from ...utils.component_utils import add_component, export_component_base, import_component_base
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.buffer_utils import determine_indices_width, parse_uint, serialize_uint
from ...utils.reference_helper import register_exported_buffer, import_buffer


_stf_type = "stfexp.mesh.seams"
_blender_property_name = "stfexp_mesh_seams"


class STFEXP_Mesh_Seams(STF_BlenderComponentBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Mesh) -> any:
	buffer_seams = BytesIO(import_buffer(context, json_resource, json_resource["seams"]))

	indices_width: int = json_resource.get("indices_width", 4)

	edge_dict: dict[int, dict[int, bpy.types.MeshEdge]] = {}
	for edge in context_object.edges:
		if(edge.vertices[0] not in edge_dict):
			edge_dict[edge.vertices[0]] = {}
		if(edge.vertices[1] not in edge_dict):
			edge_dict[edge.vertices[1]] = {}
		edge_dict[edge.vertices[0]][edge.vertices[1]] = edge
		edge_dict[edge.vertices[1]][edge.vertices[0]] = edge

	for _ in range(int((buffer_seams.getbuffer().nbytes / indices_width) / 2)):
		v0_index = parse_uint(buffer_seams, indices_width)
		v1_index = parse_uint(buffer_seams, indices_width)
		edge_dict[v0_index][v1_index].use_seam = True

	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Mesh_Seams, context_object: bpy.types.Mesh) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)

	indices_width = determine_indices_width(len(context_object.loops))

	buffer_seams = BytesIO()
	for edge in context_object.edges:
		if(edge.use_seam and not edge.is_loose):
			for edge_vertex_index in edge.vertices:
				buffer_seams.write(serialize_uint(edge_vertex_index, indices_width))
	ret["indices_width"] = indices_width
	ret["seams"] = register_exported_buffer(ret, context.serialize_buffer(buffer_seams.getvalue()))

	return ret, component.stf_id


class STF_Module_STF_Mesh_Seams(STF_BlenderComponentModule):
	"""Represents the existence of mesh-seams. If they are present, Blender will automatically create this component on export, no need to add it manually"""
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
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Mesh_Seams))

def unregister():
	if hasattr(bpy.types.Mesh, _blender_property_name):
		delattr(bpy.types.Mesh, _blender_property_name)
