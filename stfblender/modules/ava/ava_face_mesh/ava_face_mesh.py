import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component


_stf_type = "ava.face_mesh"
_blender_property_name = "stf_ava_face_mesh"


class AVA_FaceMesh(STF_BlenderComponentBase):
	pass


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_FaceMesh):
	if(not parent_application_object.data or type(parent_application_object.data) is not bpy.types.Mesh):
		layout.label(text="Warning: Component is not placed on a mesh-instance!")
	else:
		layout.label(text="This mesh instance will be used as the primary face mesh!")



def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_FaceMesh, parent_application_object: any) -> tuple[dict, str]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
	}
	return ret, application_object.stf_id


class STF_Module_AVA_FaceMesh(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_FaceMesh]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_FaceMesh
]


def register():
	bpy.types.Object.stf_ava_face_mesh = bpy.props.CollectionProperty(type=AVA_FaceMesh) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stf_ava_face_mesh"):
		del bpy.types.Object.stf_ava_face_mesh

