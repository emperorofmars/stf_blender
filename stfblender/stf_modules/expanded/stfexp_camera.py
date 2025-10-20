import bpy
import math
import re
from typing import Callable

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module import STF_Module
from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui, ensure_stf_id
from ...base.stf_report import STFReportSeverity, STFReport


_stf_type = "stfexp.camera"


class STFSetSTFEXPCameraIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Camera"""
	bl_idname = "stf.set_stfexp_camera_stf_id"
	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.Camera)
	def get_property(self, context): return context.object.stf_instance

class STFEXP_Camera_Panel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stfexp_camera_editor"
	bl_label = "STF Editor: stfexp.camera"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.Camera)

	def draw(self, context):
		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, context.object.stf_instance, STFSetSTFEXPCameraIDOperator.bl_idname, True)


"""
Import
"""

"""def _v_fov_to_h_fov(camera: bpy.types.Camera, cur_fov: float):
	if(bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y >= 1):
		if(camera.type == "ORTHO"):
			# convert vertical fov to horizontal
			return 2 * math.atan((0.5 * bpy.context.scene.render.resolution_x) / (0.5 * bpy.context.scene.render.resolution_y / math.tan(cur_fov / 2)))
		else:
			# convert vertical ortho_scale
			return cur_fov * (bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y)
	else:
	if(camera.type == "ORTHO"):
		return cur_fov
	else:
		return cur_fov"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_camera = bpy.data.cameras.new(json_resource.get("name", "STFEXP Camera"))
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_camera)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_camera))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import camera", STFReportSeverity.Error, stf_id, _stf_type, context_object))

	blender_camera.sensor_fit = "VERTICAL"

	match(json_resource.get("projection", "perspective")):
		case "perspective":
			blender_camera.type = "PERSP"
			#blender_camera.angle = _v_fov_to_h_fov(blender_camera, json_resource.get("fov", 40))
			blender_camera.angle = json_resource.get("fov", 40)
		case "orthographic":
			blender_camera.type = "ORTHO"
			#blender_camera.ortho_scale = _v_fov_to_h_fov(blender_camera, json_resource.get("fov", 40))
			blender_camera.ortho_scale = json_resource.get("fov", 40)

	return blender_object


"""
Export
"""

def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and type(application_object[1]) == bpy.types.Camera):
		return 1000
	else:
		return -1

def _is_aspect_horizontal(camera: bpy.types.Camera) -> bool:
	match(camera.sensor_fit):
		case "HORIZONTAL": return True
		case "VERTICAL": return False
		case "AUTO": return False if bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y <= 1 else True

def _h_fov_to_v_fov(camera: bpy.types.Camera, cur_angle: float, cur_ortho_scale: float) -> float:
	if(_is_aspect_horizontal(camera)):
		if(camera.type == "ORTHO"):
			# convert horizontally limited scale to vertical scale
			return cur_ortho_scale / (bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y)
		else:
			# convert horizontal fov to vertical
			return 2 * math.atan((0.5 * bpy.context.scene.render.resolution_y) / (0.5 * bpy.context.scene.render.resolution_x / math.tan(cur_angle / 2)))
	else:
		if(camera.type == "ORTHO"):
			return cur_ortho_scale
		else:
			return cur_angle

def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_camera: bpy.types.Camera = application_object[1]
	ensure_stf_id(context, blender_object.stf_instance)

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_instance.stf_name,
		"projection": "orthographic" if blender_camera.type == "ORTHO" else "perspective",
		"aspect_ratio": bpy.context.scene.render.resolution_x / bpy.context.scene.render.resolution_y,
		"fov": _h_fov_to_v_fov(blender_camera, blender_camera.angle, blender_camera.ortho_scale),
	}
	return ret, blender_object.stf_instance.stf_id


"""
Animation
"""

def _is_sensor_fit_horizontal(camera: bpy.types.Camera) -> bool:
	if(camera.sensor_fit == "VERTICAL"): return False
	else: return True


def _get__convert_lens_to_fov_func(camera: bpy.types.Camera) -> Callable:
	# let _ret
	if(camera.type == "ORTHO"):
		def _ret(value: list[float]) -> list[float]:
			return [_h_fov_to_v_fov(camera, 0, value[0])]
	else:
		def _ret(value: list[float]) -> list[float]:
			return [_h_fov_to_v_fov(camera, 2 * math.atan((camera.sensor_width if _is_sensor_fit_horizontal(camera) else camera.sensor_height) / (2 * value[0])), 0)] # convert lens to fov
	return _ret

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(application_object.data.type == "ORTHO"):
		if(match := re.search(r"^ortho_scale", data_path)):
			return [application_object.stf_info.stf_id, "instance", "fov"], _get__convert_lens_to_fov_func(application_object.data), None
	elif(application_object.data.type == "PERSP"):
		if(match := re.search(r"^lens", data_path)):
			return [application_object.stf_info.stf_id, "instance", "fov"], _get__convert_lens_to_fov_func(application_object.data), None
	# todo enabled maybe?
	return None


def _get__convert_fov_to_blender_func(camera: bpy.types.Camera) -> Callable:
	def _ret(value: list[float]) -> list[float]:
		return [(camera.sensor_width if _is_sensor_fit_horizontal(camera) else camera.sensor_height) / (2 * math.tan(value[0] / 2))] # convert fov to lens
	return _ret

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	match(stf_path[1]):
		case "fov":
			if(application_object.data.type == "ORTHO"):
				return None, 0, "CAMERA", "ortho_scale", 0, None
			elif(application_object.data.type == "PERSP"):
				return None, 0, "CAMERA", "lens", 0, _get__convert_fov_to_blender_func(application_object.data)
	return None


class STF_Module_STFEXP_Camera(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["camera"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["lens", "ortho_scale"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STFEXP_Camera
]

