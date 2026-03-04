import bpy
from typing import Any

from ....lib_stfblender import STF_Module, STF_ExportContext, STF_ExportContext, STF_ImportContext

from ....utils.component_utils import get_components_from_object
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister
from ....utils.id_utils import ensure_stf_id

# TODO this module is at a bare minimum level, improve it

_stf_type = "stfexp.text"


class STFEXP_Text(bpy.types.PropertyGroup):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	blender_text: bpy.types.TextCurve = bpy.data.curves.new(json_resource.get("name", "STF Text"), "FONT")
	blender_text.stf_info.stf_id = stf_id
	if(json_resource.get("name")):
		blender_text.stf_info.stf_name = json_resource["name"]
		blender_text.stf_info.stf_name_source_of_truth = True

	blender_text.body = json_resource.get("text", "")

	return blender_text


def _stf_export(context: STF_ExportContext, application_object: Any, context_object: Any) -> tuple[dict, str]:
	blender_text: bpy.types.TextCurve = application_object
	ensure_stf_id(context, blender_text)

	ret = {
		"type": _stf_type,
		"name": blender_text.stf_info.stf_name if blender_text.stf_info.stf_name_source_of_truth else blender_text.name,
		"text": blender_text.body
	}

	return ret, blender_text.stf_info.stf_id


class STF_Module_STFEXP_Text(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["text"]
	understood_application_types = [bpy.types.TextCurve]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STFEXP_Text
]


def register():
	bpy.types.TextCurve.stf_text = bpy.props.PointerProperty(type=STFEXP_Text)
	boilerplate_register(bpy.types.TextCurve, "data")

def unregister():
	boilerplate_unregister(bpy.types.TextCurve, "data")
	if hasattr(bpy.types.TextCurve, "stf_text"):
		del bpy.types.TextCurve.stf_text
