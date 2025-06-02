import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component


_stf_type = "ava.visemes.mapping"
_blender_property_name = "stf_ava_visemes_mapping"


class AVA_Visemes_Mapping(STF_BlenderComponentBase):
	mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Visemes Mesh Instance") # type: ignore
	visemes_component: bpy.props.StringProperty(name="Visemes Component") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_Visemes_Mapping):
	layout.prop(component, "mesh_instance")
	layout.prop(component, "visemes_component")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)

	if("target" in json_resource):
		if(len(json_resource["target"]) > 0):
			def _handle_delayed():
				component.mesh_instance = context.get_imported_resource(json_resource["target"][0])
			context.add_task(_handle_delayed)
		
		if(len(json_resource["target"]) == 4):
			component.visemes_component = json_resource["target"][3]

	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Visemes_Mapping, parent_application_object: any) -> tuple[dict, str]:
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
	}
	if(application_object.mesh_instance and application_object.visemes_component):
		ret["target"] = [application_object.mesh_instance.stf_id, "instance", "components", application_object.visemes_component]
	elif(application_object.mesh_instance):
		ret["target"] = [application_object.mesh_instance.stf_id]

	return ret, application_object.stf_id


class STF_Module_AVA_Visemes_Mapping(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_Visemes_Mapping]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_Visemes_Mapping
]


def register():
	bpy.types.Collection.stf_ava_visemes_mapping = bpy.props.CollectionProperty(type=AVA_Visemes_Mapping) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_ava_visemes_mapping"):
		del bpy.types.Collection.stf_ava_visemes_mapping

