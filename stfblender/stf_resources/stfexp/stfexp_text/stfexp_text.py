import bpy
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_Handler_BlenderNative, STF_Handler_ComponentHolder, boilerplate_register, boilerplate_unregister, get_components_from_object, ensure_stf_id
from .stfexp_text_ui import STFAddTextComponentOperator, STFEditTextComponentIdOperator, STFRemoveTextComponentOperator, STFSetTextIDOperator

# TODO this module is at a bare minimum level, improve it

_stf_type = "stfexp.text"


class STFEXP_Text(bpy.types.PropertyGroup):
	pass


class Handler_STFEXP_Text(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["text"]
	understood_blender_types = [bpy.types.TextCurve]

	operator_set_stf_id = STFSetTextIDOperator.bl_idname

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
		blender_text: bpy.types.TextCurve = bpy.data.curves.new(json_resource.get("name", "STF Text"), "FONT")  # pyright: ignore[reportAssignmentType]
		blender_text.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			blender_text.stf_info.stf_name = json_resource["name"]
			blender_text.stf_info.stf_name_source_of_truth = True

		blender_text.body = json_resource.get("text", "")
		return blender_text

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str]:
		blender_text: bpy.types.TextCurve = blender_resource
		ensure_stf_id(context, blender_text)

		ret = {
			"type": _stf_type,
			"name": blender_text.stf_info.stf_name if blender_text.stf_info.stf_name_source_of_truth else blender_text.name,
			"text": blender_text.body
		}
		return ret, blender_text.stf_info.stf_id


	get_components = get_components_from_object
	operator_component_add = STFAddTextComponentOperator.bl_idname
	operator_component_remove = STFRemoveTextComponentOperator.bl_idname
	operator_component_edit = STFEditTextComponentIdOperator.bl_idname

register_stf_handlers = [
	Handler_STFEXP_Text
]


def register():
	bpy.types.TextCurve.stf_text = bpy.props.PointerProperty(type=STFEXP_Text)
	boilerplate_register(bpy.types.TextCurve)

def unregister():
	boilerplate_unregister(bpy.types.TextCurve)
	if hasattr(bpy.types.TextCurve, "stf_text"):
		del bpy.types.TextCurve.stf_text
