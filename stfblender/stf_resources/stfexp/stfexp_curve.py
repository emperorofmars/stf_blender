import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_Handler_BlenderNative, STF_Handler_ComponentHolder, STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase, boilerplate_register, boilerplate_unregister, get_components_from_object, ensure_stf_id


class STFSetCurveIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Curve"""
	bl_idname = "stf.set_curve_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.Curve)
	def get_property(self, context): return context.curve.stf_info

class STFAddCurveComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Curve"""
	bl_idname = "stf.add_curve_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.Curve)
	def get_property(self, context): return context.curve

class STFRemoveCurveComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Curve"""
	bl_idname = "stf.remove_curve_component"
	def get_property(self, context): return context.curve

class STFEditCurveComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_curve_component_id"
	def get_property(self, context): return context.curve


class Handler_STFEXP_Curve(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = "stfexp.curve"
	stf_category = STF_Category.DATA
	like_types = ["curve"]
	understood_blender_types = [bpy.types.Curve]

	operator_set_stf_id = STFSetCurveIDOperator.bl_idname

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
		blender_curve: bpy.types.Curve = bpy.data.curves.new(json_resource.get("name", "STF Curve"), "CURVE") # pyright: ignore[reportAssignmentType]
		blender_curve.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			blender_curve.stf_info.stf_name = json_resource["name"]
			blender_curve.stf_info.stf_name_source_of_truth = True

		#TODO

		return blender_curve

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: bpy.types.Curve, context_resource: Any) -> tuple[dict, str]:
		ensure_stf_id(context, blender_resource)
		ret = {
			"type": Handler_STFEXP_Curve.stf_type,
			"name": blender_resource.stf_info.stf_name if blender_resource.stf_info.stf_name_source_of_truth else blender_resource.name
		}

		#TODO

		return ret, blender_resource.stf_info.stf_id

	get_components = get_components_from_object
	operator_component_add = STFAddCurveComponentOperator.bl_idname
	operator_component_remove = STFRemoveCurveComponentOperator.bl_idname
	operator_component_edit = STFEditCurveComponentIdOperator.bl_idname


def register():
	boilerplate_register(bpy.types.Curve)

def unregister():
	boilerplate_unregister(bpy.types.Curve)
