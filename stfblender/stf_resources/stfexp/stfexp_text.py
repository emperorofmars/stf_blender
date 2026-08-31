import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_Handler_BlenderNative, STF_Handler_ComponentHolder, STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase, get_components_from_object, ensure_stf_id


class STFSetTextIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Text"""
	bl_idname = "stf.set_text_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)
	def get_property(self, context): return context.curve.stf_info

class STFAddTextComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Text"""
	bl_idname = "stf.add_text_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)
	def get_property(self, context): return context.curve

class STFRemoveTextComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Text"""
	bl_idname = "stf.remove_text_component"
	def get_property(self, context): return context.curve

class STFEditTextComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_text_component_id"
	def get_property(self, context): return context.curve

# TODO this module is at a bare minimum level, improve it


class STFEXP_Text(bpy.types.PropertyGroup):
	pass


class Handler_STFEXP_Text(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = "stfexp.text"
	stf_category = STF_Category.DATA
	like_types = ["text"]
	understood_blender_types = [bpy.types.TextCurve]

	operator_set_stf_id = STFSetTextIDOperator.bl_idname

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
		blender_text: bpy.types.TextCurve = bpy.data.curves.new(json_resource.get("name", "STF Text"), "FONT") # pyright: ignore[reportAssignmentType]
		blender_text.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			blender_text.stf_info.stf_name = json_resource["name"]
			blender_text.stf_info.stf_name_source_of_truth = True

		blender_text.body = json_resource.get("text", "")
		return blender_text

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: bpy.types.TextCurve, context_resource: Any) -> tuple[dict, str]:
		ensure_stf_id(context, blender_resource)
		ret = {
			"type": cls.stf_type,
			"name": blender_resource.stf_info.stf_name if blender_resource.stf_info.stf_name_source_of_truth else blender_resource.name,
			"text": blender_resource.body
		}
		return ret, blender_resource.stf_info.stf_id

	get_components = get_components_from_object
	operator_component_add = STFAddTextComponentOperator.bl_idname
	operator_component_remove = STFRemoveTextComponentOperator.bl_idname
	operator_component_edit = STFEditTextComponentIdOperator.bl_idname
