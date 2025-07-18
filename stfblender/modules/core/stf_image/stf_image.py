import bpy
import pathlib

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....core.stf_module import STF_Module
from ....core.stf_report import STFReport, STFReportSeverity
from ....utils.component_utils import get_components_from_object
from ....utils.id_utils import ensure_stf_id
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister


_stf_type = "stf.image"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_image = bpy.data.images.new(json_resource.get("name", "STF Image"), 8, 8)
	blender_image.stf_id = stf_id
	if(json_resource.get("name")):
		blender_image.stf_name = json_resource["name"]
		blender_image.stf_name_source_of_truth = True

	image_buffer = context.import_buffer(json_resource["buffer"])
	blender_image.pack(data=image_buffer, data_len=len(image_buffer))
	blender_image.source = "FILE"

	if("data_type" in json_resource):
		if(json_resource["data_type"] == "non_color"):
			blender_image.colorspace_settings.name = "Non-Color"

	return blender_image


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_image: bpy.types.Image = application_object
	ensure_stf_id(context, blender_image)

	try:
		## let image_bytes: bytes
		## let image_format: str
		if(blender_image.packed_file):
			image_bytes = blender_image.packed_file.data
			image_format = blender_image.file_format.lower()
		else:
			image_bytes = pathlib.Path(bpy.path.abspath(blender_image.filepath)).resolve().read_bytes()
			image_format = pathlib.Path(blender_image.filepath).suffix[1:].lower() if pathlib.Path(blender_image.filepath).suffix.startswith(".") else pathlib.Path(blender_image.filepath).suffix.lower()
		buffer_id = context.serialize_buffer(image_bytes)

		ret = {
			"type": _stf_type,
			"name": blender_image.stf_name if blender_image.stf_name_source_of_truth else blender_image.name,
			"format": image_format,
			"buffer": buffer_id,
			"data_type": "non_color" if blender_image.colorspace_settings.name == "Non-Color" else "color"
		}

		return ret, blender_image.stf_id
	except Exception as error:
		context.report(STFReport("Could not export image: " + str(blender_image.filepath), STFReportSeverity.Error, blender_image.stf_id, _stf_type, blender_image))
		return None


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
