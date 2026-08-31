import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_Handler_BlenderNative, STF_Handler_ComponentHolder, STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase, STFReport, STFReportSeverity, get_components_from_object, ensure_stf_id
from ....stfblender_common.utils import trs_utils


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
	"""2D and 3D Bézier Curves in 3D space"""
	stf_type = "stfexp.curve"
	stf_category = STF_Category.DATA
	like_types = ["curve"]
	understood_blender_types = [bpy.types.Curve]

	operator_set_stf_id = STFSetCurveIDOperator.bl_idname

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
		blender_curve: bpy.types.Curve = bpy.data.curves.new(json_resource.get("name", "STF Curve"), "CURVE")
		blender_curve.stf_info.stf_id = stf_id
		if(json_resource.get("name")):
			blender_curve.stf_info.stf_name = json_resource["name"]
			blender_curve.stf_info.stf_name_source_of_truth = True

		blender_curve.dimensions = "2D" if json_resource.get("dimensions", 2) == 2 else "3D"

		for json_spline in json_resource.get("splines", []):
			if(json_spline.get("type") == "bezier"):
				blender_spline = blender_curve.splines.new("BEZIER")
				blender_spline.use_cyclic_u = json_spline.get("cyclic", False)

				points_to_add = len(json_spline.get("points", [])) - len(blender_spline.bezier_points) # blender why
				if(points_to_add > 0):
					blender_spline.bezier_points.add(points_to_add)

				for point_index, json_point in enumerate(json_spline.get("points", [])):
					point = blender_spline.bezier_points[point_index]
					point.co = trs_utils.stf_translation_to_blender(json_point["translation"])
					point.handle_left = trs_utils.stf_translation_to_blender(json_point["handle_in"])
					point.handle_left_type = handle_conversion_to_blender(json_point["handle_in_type"])
					point.handle_right = trs_utils.stf_translation_to_blender(json_point["handle_out"])
					point.handle_right_type = handle_conversion_to_blender(json_point["handle_out_type"])
					point.tilt = json_point["tilt"]

		# TODO shape keys maybe ??

		return blender_curve

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: bpy.types.Curve, context_resource: Any) -> tuple[dict, str]:
		ensure_stf_id(context, blender_resource)

		splines = []
		ret = {
			"type": Handler_STFEXP_Curve.stf_type,
			"name": blender_resource.stf_info.stf_name if blender_resource.stf_info.stf_name_source_of_truth else blender_resource.name,
			"dimensions": 2 if blender_resource.dimensions == "2D" else 3,
			"splines": splines,
		}

		if(blender_resource.splines):
			for spline in blender_resource.splines:
				if(spline.type == "BEZIER"):
					points = []
					for point in spline.bezier_points:
						points.append({
							"translation": trs_utils.blender_translation_to_stf(point.co),
							"handle_in": trs_utils.blender_translation_to_stf(point.handle_left),
							"handle_in_type": handle_conversion_to_stf(point.handle_left_type),
							"handle_out": trs_utils.blender_translation_to_stf(point.handle_right),
							"handle_out_type": handle_conversion_to_stf(point.handle_right_type),
							"tilt": point.tilt,
						})
					splines.append({
						"type": "bezier",
						"points": points,
						"cyclic": spline.use_cyclic_u
					})
				else:
					context.report(STFReport(f"Unsupported spline type: {spline.type}", STFReportSeverity.Info, blender_resource.stf_info.stf_id, cls.stf_type, blender_resource))

		# TODO shape keys maybe ??

		return ret, blender_resource.stf_info.stf_id

	get_components = get_components_from_object
	operator_component_add = STFAddCurveComponentOperator.bl_idname
	operator_component_remove = STFRemoveCurveComponentOperator.bl_idname
	operator_component_edit = STFEditCurveComponentIdOperator.bl_idname

	# TODO animation with hook objects (blender why so complicated?)


def handle_conversion_to_stf(blender_handle: str):
	match blender_handle:
		case "FREE": return "free"
		case "VECTOR": return "free"
		case "ALIGNED": return "aligned"
		case "AUTO": return "auto"
		case _: return "free"

def handle_conversion_to_blender(stf_handle: str):
	match stf_handle:
		case "free": return "FREE"
		case "aligned": return "ALIGNED"
		case "auto": return "AUTO"
		case _: return "FREE"
