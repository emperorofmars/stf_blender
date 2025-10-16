import bpy
import math
import re
from typing import Callable

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
			if(bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y <= 1):
				# vertical fov
				blender_camera.angle = json_resource.get("fov", 40)
			else:
				# convert vertical fov to horizontal
				blender_camera.angle = 2 * math.atan((0.5 * bpy.context.scene.render.resolution_x) / (0.5 * bpy.context.scene.render.resolution_y / math.tan(angle / 2)))
		case "orthographic":
			blender_camera.type = "ORTHO"
			# convert vertical ortho_scale
			blender_camera.ortho_scale = json_resource.get("fov", 6) * (bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y)

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

	fov_source_aspect = "vertical"
	match(blender_camera.sensor_fit):
		case "HORIZONTAL": fov_source_aspect = "horizontal"
		case "VERTICAL": fov_source_aspect = "vertical"
		case "AUTO": fov_source_aspect = "vertical" if bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y <= 1 else "horizontal"

	stf_fov = blender_camera.angle
	if(fov_source_aspect == "horizontal"):
		if(blender_camera.type == "ORTHO"):
			# convert horizontally limited scale to vertical scale
			stf_fov = blender_camera.ortho_scale / (bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y)
		else:
			# convert horizontal fov to vertical
			stf_fov = 2 * math.atan((0.5 * bpy.context.scene.render.resolution_y) / (0.5 * bpy.context.scene.render.resolution_x / math.tan(blender_camera.angle / 2)))
	else:
		if(blender_camera.type == "ORTHO"):
			stf_fov = blender_camera.ortho_scale
		else:
			stf_fov = blender_camera.angle

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_instance.stf_name,
		"projection": "orthographic" if blender_camera.type == "ORTHO" else "perspective",
		"aspect_ratio": bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y,
		"fov": stf_fov,
	}

	return ret, blender_object.stf_instance.stf_id


def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^lens", data_path)):
		return ["enabled"], None, None
	if(match := re.search(r"^ortho_scale", data_path)):
		return ["enabled"], None, None
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	match(stf_path[1]):
		case "weight":
			return None, 0, "CAMERA", "lens", 0, None
		case "enabled":
			return None, 0, "CAMERA", "ortho_scale", 0, None
	return None


class STF_Module_STFEXP_Camera(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["camera"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func

	# todo
	"""understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["lens", "ortho_scale"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func"""


register_stf_modules = [
	STF_Module_STFEXP_Camera
]

