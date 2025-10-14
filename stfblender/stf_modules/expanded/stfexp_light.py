import bpy

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module import STF_Module
from ...utils.id_utils import ensure_stf_id
from ...base.stf_report import STFReportSeverity, STFReport


_stf_type = "stfexp.light"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_light_type = "POINT"
	match(json_resource.get("light_type")):
		case "point":
			blender_light_type = "POINT"
		case "directional":
			blender_light_type = "SUN"
		case "spot":
			blender_light_type = "SPOT"
		case "area":
			blender_light_type = "AREA"

	blender_light = bpy.data.lights.new(json_resource.get("name", "STFEXP Light"), blender_light_type)
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_light)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_light))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import light", STFReportSeverity.Error, stf_id, _stf_type, context_object))

	if("brightness" in json_resource): blender_light.energy = json_resource["brightness"]
	if("color" in json_resource): blender_light.color = tuple(json_resource["color"])
	if("temperature" in json_resource): blender_light.temperature = json_resource["temperature"]

	match(blender_light.type):
		case "point":
			if("radius" in json_resource): blender_light.shadow_soft_size = json_resource["radius"]
		case "directional":
			pass
		case "spot":
			if("radius" in json_resource): blender_light.shadow_soft_size = json_resource["radius"]
			if("angle" in json_resource): blender_light.spot_size = json_resource["angle"]
		case "area":
			match(json_resource.get("area_shape", "square")):
				case "square":
					blender_light.shape = "SQUARE"
					if("size" in json_resource): blender_light.size = json_resource["size"]
				case "disc":
					blender_light.shape = "DISK"
					if("size" in json_resource): blender_light.size = json_resource["size"]
				case "rectangle":
					blender_light.shape = "RECTANGLE"
					if("width" in json_resource): blender_light.size = json_resource["width"]
					if("height" in json_resource): blender_light.size_y = json_resource["height"]
				case "ellipsis":
					blender_light.shape = "ELLIPSE"
					if("width" in json_resource): blender_light.size = json_resource["width"]
					if("height" in json_resource): blender_light.size_y = json_resource["height"]

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and isinstance(application_object[1], bpy.types.Light)):
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
			ret["radius"] = blender_light.shadow_soft_size
		case "SUN":
			ret["light_type"] = "directional"
		case "SPOT":
			ret["light_type"] = "spot"
			ret["radius"] = blender_light.shadow_soft_size
			ret["angle"] = blender_light.spot_size
		case "AREA":
			ret["light_type"] = "area"
			match(blender_light.shape):
				case "SQUARE":
					ret["area_shape"] = "square"
					ret["size"] = blender_light.size
				case "DISK":
					ret["area_shape"] = "disc"
					ret["size"] = blender_light.size
				case "RECTANGLE":
					ret["area_shape"] = "rectangle"
					ret["width"] = blender_light.size
					ret["height"] = blender_light.size_y
				case "ELLIPSE":
					ret["area_shape"] = "ellipsis"
					ret["width"] = blender_light.size
					ret["height"] = blender_light.size_y

	ret["brightness"] = blender_light.energy
	ret["color"] = blender_light.color[:]
	if(blender_light.use_temperature):
		ret["temperature"] = blender_light.temperature

	return ret, blender_object.stf_instance.stf_id


# todo animation support for lens/angle values


class STF_Module_STFEXP_Light(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["light"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func


register_stf_modules = [
	STF_Module_STFEXP_Light
]

