import bpy

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_module import STF_Module
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.boilerplate import boilerplate_register, boilerplate_unregister


_stf_type = "stf.image"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_image = bpy.data.images.new(json_resource.get("name", "STF Image"), 1024, 1024)
	blender_image.stf_id = stf_id
	if(json_resource.get("name")):
		blender_image.stf_name = json_resource["name"]
		blender_image.stf_name_source_of_truth = True

	return blender_image


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_image: bpy.types.Image = application_object
	ensure_stf_id(context, blender_image)

	ret = {
		"type": _stf_type,
		"name": blender_image.stf_name if blender_image.stf_name_source_of_truth else blender_image.name,
	}

	return ret, blender_image.stf_id


class STF_Module_STF_Image(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["image"]
	understood_application_types = [bpy.types.Image]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Image
]


def register():
	boilerplate_register(bpy.types.Image, "data")

def unregister():
	boilerplate_unregister(bpy.types.Image, "data")
