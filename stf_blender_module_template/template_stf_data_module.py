import bpy
from typing import Any

from .stf_dependency_import import stfblender


_stf_type = "my_custom.namespaced.brush"


def _stf_import(context: stfblender.common.STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	application_object = bpy.data.brushes.new(json_resource.get("name", "My Custom Brush"))
	application_object.stf_info.stf_id = stf_id
	if(json_resource.get("name")):
		application_object.stf_info.stf_name = json_resource["name"]
		application_object.stf_info.stf_name_source_of_truth = True

	# TODO Do most of the import

	return application_object


def _stf_export(context: stfblender.common.STF_ExportContext, application_object: Any, context_object: Any) -> tuple[dict, str]:
	application_object: bpy.types.Brush = application_object
	stfblender.common.utils.id_utils.ensure_stf_id(context, application_object)

	json_resource = {
		"type": _stf_type,
		"name": application_object.stf_info.stf_name if application_object.stf_info.stf_name_source_of_truth else application_object.name,
	}

	# TODO Do most of the export

	return json_resource, application_object.stf_info.stf_id


class CustomSTFBrushModule(stfblender.common.STF_Module):
	stf_type = _stf_type
	stf_category = "data"
	like_types = ["brush", "or", "whatever"]
	priority = 0
	understood_application_types = [bpy.types.Brush]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = stfblender.common.module_component.component_utils.get_components_from_object


register_stf_modules = [CustomSTFBrushModule]


def register():
	stfblender.common.utils.boilerplate.boilerplate_register(bpy.types.Brush, "data")

def unregister():
	stfblender.common.utils.boilerplate.boilerplate_unregister(bpy.types.Brush, "data")
