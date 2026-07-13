import bpy
from typing import Any

from .stf_dependency_import import stfblender


_stf_type = "my_custom.namespaced.brush"


def _stf_import(context: stfblender.common.STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	blender_object = bpy.data.brushes.new(json_resource.get("name", "My Custom Brush"))
	blender_object.stf_info.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_info.stf_name = json_resource["name"]
		blender_object.stf_info.stf_name_source_of_truth = True

	# TODO Do most of the import

	return blender_object


def _stf_export(context: stfblender.common.STF_ExportContext, blender_object: Any, context_object: Any) -> tuple[dict, str]: # pyright: ignore[reportRedeclaration]
	blender_object: bpy.types.Brush = blender_object
	stfblender.common.ensure_stf_id(context, blender_object)

	json_resource = {
		"type": _stf_type,
		"name": blender_object.stf_info.stf_name if blender_object.stf_info.stf_name_source_of_truth else blender_object.name,
	}

	# TODO Do most of the export

	return json_resource, blender_object.stf_info.stf_id


# TODO stf set id operator

# TODO draw gui


class CustomSTFBrushHandler(stfblender.common.STF_Handler_Data, stfblender.common.STF_HandlerComponents):
	stf_type = _stf_type
	stf_category = "data"
	like_types = ["brush", "or", "whatever"]
	priority = 0
	understood_application_types = [bpy.types.Brush]
	import_func = _stf_import
	export_func = _stf_export

	get_components_func = stfblender.common.get_components_from_object


def register():
	stfblender.common.boilerplate_register(bpy.types.Brush)

def unregister():
	stfblender.common.boilerplate_unregister(bpy.types.Brush)
