import bpy

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module import STF_Module
from ...utils.id_utils import ensure_stf_id
from ...base.stf_report import STFReportSeverity, STFReport


_stf_type = "stfexp.camera"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_camera = bpy.data.cameras.new(json_resource.get("name", "STFEXP Camera"))
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_camera)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_camera))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import camera", STFReportSeverity.Error, stf_id, _stf_type, context_object))

	match(json_resource.get("projection", "perspective")):
		case "perspective":
			blender_camera.type = "PERSP"
			blender_camera.angle = json_resource.get("fov", 40)
		case "orthographic":
			blender_camera.type = "ORTHO"
			blender_camera.ortho_scale = json_resource.get("fov", 6)

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and type(application_object[1]) == bpy.types.Camera):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_camera: bpy.types.Camera = application_object[1]
	ensure_stf_id(context, blender_object.stf_instance)

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_instance.stf_name,
		"projection": "orthographic" if blender_camera.type == "ORTHO" else "perspective",
		"fov": blender_camera.ortho_scale if blender_camera.type == "ORTHO" else blender_camera.angle,
	}

	return ret, blender_object.stf_instance.stf_id


# todo animation support for lens/angle values


class STF_Module_STFEXP_Camera(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["camera"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func


register_stf_modules = [
	STF_Module_STFEXP_Camera
]

