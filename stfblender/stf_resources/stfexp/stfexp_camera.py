import bpy
import math
import re
from typing import Any, Callable

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STF_Handler_Animation, STF_Handler_BlenderNative, STFReportSeverity, STFReport, STFSetIDOperatorBase, ensure_stf_id


_stf_type = "stfexp.camera"


class STFSetSTFEXPCameraIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Camera"""
	bl_idname = "stf.set_stfexp_camera_stf_id"
	@classmethod
	def poll(cls, context) -> bool: return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.Camera)  # pyright: ignore[reportReturnType]
	def get_property(self, context): return context.object.stf_instance


"""
Import
"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
	blender_camera = bpy.data.cameras.new(json_resource.get("name", "STFEXP Camera"))
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_camera)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_camera))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import camera", STFReportSeverity.Error, stf_id, _stf_type, context_resource))

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

def _can_handle_blender_resource(blender_resource: Any) -> int:
	if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and type(blender_resource[1]) is bpy.types.Camera):
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

def _stf_export(context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = blender_resource[0]
	blender_camera: bpy.types.Camera = blender_resource[1]
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

def _export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(blender_resource.data.type == "ORTHO"):
		if(match := re.search(r"^ortho_scale", blender_property_path)):
			return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "fov"], _get__convert_lens_to_fov_func(blender_resource.data))
	elif(blender_resource.data.type == "PERSP"):
		if(match := re.search(r"^lens", blender_property_path)):
			return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "fov"], _get__convert_lens_to_fov_func(blender_resource.data))
	# todo enabled maybe?
	return None


def _get__convert_fov_to_blender_func(camera: bpy.types.Camera) -> Callable:
	def _ret(value: list[float]) -> list[float]:
		return [(camera.sensor_width if _is_sensor_fit_horizontal(camera) else camera.sensor_height) / (2 * math.tan(value[0] / 2))] # convert fov to lens
	return _ret

def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
	match(stf_property_path[1]):
		case "fov":
			if(blender_resource.data.type == "ORTHO"):
				return BlenderPropertyPathPart("CAMERA", "ortho_scale")
			elif(blender_resource.data.type == "PERSP"):
				return BlenderPropertyPathPart("CAMERA", "lens", _get__convert_fov_to_blender_func(blender_resource.data))
	return None


"""
Definition
"""

class Handler_STFEXP_Camera(STF_Handler_BlenderNative, STF_Handler_Animation):
	stf_type = _stf_type
	stf_category = STF_Category.INSTANCE
	like_types = ["camera"]
	understood_blender_types = [tuple]
	import_resource = _stf_import
	export_resource = _stf_export
	can_handle_blender_resource = _can_handle_blender_resource
	get_stf_prop_holder = lambda bo: bo[0].stf_instance
	operator_set_stf_id = STFSetSTFEXPCameraIDOperator.bl_idname

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = ["lens", "ortho_scale"]
	export_blender_animation = _export_blender_animation
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func


register_stf_handlers = [
	Handler_STFEXP_Camera
]
