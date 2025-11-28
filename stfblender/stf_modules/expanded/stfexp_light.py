import bpy
import re
from typing import Callable

from ...base.property_path_part import STFPropertyPathPart

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module import STF_Module
from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui, ensure_stf_id
from ...base.stf_report import STFReportSeverity, STFReport


_stf_type = "stfexp.light"


class STFSetSTFEXPLightIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Light"""
	bl_idname = "stf.set_stfexp_light_stf_id"
	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.Light)
	def get_property(self, context): return context.object.stf_instance

class STFEXP_Light_Panel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stfexp_light_editor"
	bl_label = "STF Editor: stfexp.light"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.Light)

	def draw(self, context):
		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, context.object.stf_instance, STFSetSTFEXPLightIDOperator.bl_idname, True)


"""
Import
"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
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
		context.report(STFReport("Failed to import light", STFReportSeverity.Error, stf_id, _stf_type, context_object))

	# todo figure out energy conversion
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

def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and isinstance(application_object[1], bpy.types.Light) and application_object[1].type in ["POINT", "SUN", "SPOT"]):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_light: bpy.types.Light = application_object[1]
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

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	if(match := re.search(r"^temperature", data_path)):
		return STFPropertyPathPart([application_object.stf_info.stf_id, "instance", "temperature"])
	elif(match := re.search(r"^color", data_path)):
		return STFPropertyPathPart([application_object.stf_info.stf_id, "instance", "color"])
	elif(match := re.search(r"^energy", data_path)):
		return STFPropertyPathPart([application_object.stf_info.stf_id, "instance", "brightness"]) # todo converter
	elif(match := re.search(r"^shadow_soft_size", data_path)):
		return STFPropertyPathPart([application_object.stf_info.stf_id, "instance", "range"])
	elif(match := re.search(r"^spot_size", data_path)):
		return STFPropertyPathPart([application_object.stf_info.stf_id, "instance", "spot_angle"])
	# todo enabled maybe?
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	match(stf_path[1]):
		case "temperature":
			return None, 0, "LIGHT", "temperature", 0, None
		case "color":
			return None, 0, "LIGHT", "color", 0, None
		case "brightness":
			return None, 0, "LIGHT", "energy", 0, None # todo converter
		case "range":
			return None, 0, "LIGHT", "shadow_soft_size", 0, None
		case "spot_angle":
			return None, 0, "LIGHT", "spot_size", 0, None
	return None


"""
Definition
"""

class STF_Module_STFEXP_Light(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["light"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["temperature", "color", "energy", "shadow_soft_size", "spot_size"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STFEXP_Light
]

def register():
	pass

def unregister():
	pass
