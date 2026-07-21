import bpy
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STFReportSeverity, STFReport, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STF_Handler_Animation, STF_Handler_BlenderNative, STFSetIDOperatorBase, ensure_stf_id


_stf_type = "stfexp.light"


class STFSetSTFEXPLightIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Light"""
	bl_idname = "stf.set_stfexp_light_stf_id"
	@classmethod
	def poll(cls, context) -> bool: return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.Light)  # pyright: ignore[reportReturnType]
	def get_property(self, context): return context.object.stf_instance

"""
Import
"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
	blender_light_type = "POINT"
	match(json_resource.get("light_type")):
		case "point":
			blender_light_type = "POINT"
		case "directional":
			blender_light_type = "SUN"
		case "spot":
			blender_light_type = "SPOT"

	blender_light = bpy.data.lights.new(json_resource.get("name", "STFEXP Light"), blender_light_type)
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_light)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_light))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		return STFReport("Failed to import light", STFReportSeverity.Error, stf_id, _stf_type, context_resource)

	# todo figure out energy conversion properly
	if("brightness" in json_resource): blender_light.energy = json_resource["brightness"]
	if("color" in json_resource): blender_light.color = tuple(json_resource["color"])
	if("temperature" in json_resource): blender_light.temperature = json_resource["temperature"]

	match(json_resource.get("light_type")):
		case "point":
			if("range" in json_resource): blender_light.shadow_soft_size = json_resource["range"]
		case "spot":
			if("range" in json_resource): blender_light.shadow_soft_size = json_resource["range"]
			if("spot_angle" in json_resource): blender_light.spot_size = json_resource["spot_angle"]
		case "directional":
			pass

	if("shadow" in json_resource): blender_light.use_shadow = json_resource["shadow"]

	return blender_object


"""
Export
"""

def _can_handle_blender_resource(blender_resource: Any) -> int:
	if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and isinstance(blender_resource[1], bpy.types.Light) and blender_resource[1].type in ["POINT", "SUN", "SPOT"]):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = blender_resource[0]
	blender_light: bpy.types.Light = blender_resource[1]
	ensure_stf_id(context, blender_object.stf_instance)

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_instance.stf_name,
	}

	match(blender_light.type):
		case "POINT":
			ret["light_type"] = "point"
			ret["range"] = blender_light.shadow_soft_size
		case "SUN":
			ret["light_type"] = "directional"
		case "SPOT":
			ret["light_type"] = "spot"
			ret["range"] = blender_light.shadow_soft_size
			ret["spot_angle"] = blender_light.spot_size

	# todo figure out energy conversion properly
	ret["brightness"] = blender_light.energy * 2 ** blender_light.exposure
	ret["color"] = blender_light.color[:]
	if(blender_light.use_temperature):
		ret["temperature"] = blender_light.temperature
	ret["shadow"] = blender_light.use_shadow

	return ret, blender_object.stf_instance.stf_id


"""
Animation
"""

def _export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(match := re.search(r"^temperature", blender_property_path)):
		return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "temperature"])
	elif(match := re.search(r"^color", blender_property_path)):
		return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "color"])
	elif(match := re.search(r"^energy", blender_property_path)):
		return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "brightness"]) # todo converter
	elif(match := re.search(r"^shadow_soft_size", blender_property_path)):
		return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "range"])
	elif(match := re.search(r"^spot_size", blender_property_path)):
		return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "spot_angle"])
	# todo enabled maybe?
	return None


def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
	match(stf_property_path[1]):
		case "temperature":
			return BlenderPropertyPathPart("LIGHT", "temperature")
		case "color":
			return BlenderPropertyPathPart("LIGHT", "color")
		case "brightness":
			return BlenderPropertyPathPart("LIGHT", "energy") # todo converter
		case "range":
			return BlenderPropertyPathPart("LIGHT", "shadow_soft_size")
		case "spot_angle":
			return BlenderPropertyPathPart("LIGHT", "spot_size")
	return None


"""
Definition
"""

class Handler_STFEXP_Light(STF_Handler_BlenderNative, STF_Handler_Animation):
	stf_type = _stf_type
	stf_category = STF_Category.INSTANCE
	like_types = ["light"]
	understood_blender_types = [tuple]
	import_resource = _stf_import
	export_resource = _stf_export
	can_handle_blender_resource = _can_handle_blender_resource
	get_stf_prop_holder = lambda blender_resource: blender_resource[0].stf_instance
	operator_set_stf_id = STFSetSTFEXPLightIDOperator.bl_idname

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = ["temperature", "color", "energy", "shadow_soft_size", "spot_size"]
	export_blender_animation = _export_blender_animation
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func


register_stf_handlers = [
	Handler_STFEXP_Light
]

def register():
	pass

def unregister():
	pass
