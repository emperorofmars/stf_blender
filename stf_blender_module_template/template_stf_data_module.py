import bpy

from .stf_dependency_import import stfblender


_stf_type = "my_custom.namespaced.brush"


def _stf_import(context: stfblender.importer.stf_import_context.STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	application_object = bpy.data.brushes.new(json_resource.get("name", "My Custom Brush"))
	application_object.stf_id = id
	if(json_resource.get("name")):
		application_object.stf_name = json_resource["name"]
		application_object.stf_name_source_of_truth = True

	# TODO Do most of the import

	return application_object


def _stf_export(context: stfblender.exporter.stf_export_context.STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	application_object: bpy.types.Brush = application_object
	stfblender.utils.id_utils.ensure_stf_id(context, application_object)

	json_resource = {
		"type": _stf_type,
		"name": application_object.stf_name if application_object.stf_name_source_of_truth else application_object.name,
	}

	# TODO Do most of the export

	return json_resource, application_object.stf_id


class CustomSTFBrushModule(stfblender.core.stf_module.STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["brush", "or", "whatever"]
	priority = 0
	understood_application_types = [bpy.types.Brush]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = stfblender.utils.component_utils.get_components_from_object


register_stf_modules = [CustomSTFBrushModule]


def register():
	stfblender.utils.boilerplate.boilerplate_register(bpy.types.Brush, "data")

def unregister():
	stfblender.utils.boilerplate.boilerplate_unregister(bpy.types.Brush, "data")
