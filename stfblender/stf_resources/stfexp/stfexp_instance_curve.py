import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STFReportSeverity, STFReport, STF_Category, STF_Handler_BlenderNative, STFSetIDOperatorBase, ensure_stf_id

# TODO this module is at a bare minimum level, improve it


class STFSetSTFEXPInstanceCurveIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Curve Instance"""
	bl_idname = "stf.set_stfexp_instance_curve_stf_id"
	@classmethod
	def poll(cls, context) -> bool: return context.object.stf_instance is not None and context.object.data is not None and isinstance(context.object.data, bpy.types.Curve)
	def get_property(self, context): return context.object.stf_instance


class Handler_STFEXP_Instance_Curve(STF_Handler_BlenderNative):
	stf_type = "stfexp.instance.curve"
	stf_category = STF_Category.INSTANCE
	like_types = ["instance.curve"]
	understood_blender_types = [tuple]
	operator_set_stf_id = STFSetSTFEXPInstanceCurveIDOperator.bl_idname
	get_stf_prop_holder = lambda blender_resource: blender_resource[0].stf_instance

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> tuple[bpy.types.Object, bpy.types.Curve] | STFReport:
		blender_curve: bpy.types.Curve | None = context.import_resource(json_resource, json_resource["curve"], STF_Category.DATA)
		if(type(blender_curve) is not bpy.types.Curve):
			return STFReport("Failed to import curve", STFReportSeverity.Error, stf_id, cls.stf_type, context_resource)

		blender_object = bpy.data.objects.new(json_resource.get("name", "STFEXP Instance Curve"), blender_curve)
		blender_object.stf_instance.stf_id = stf_id
		if(json_resource.get("name")):
			blender_object.stf_instance.stf_name = json_resource["name"]
		context.register_imported_resource(stf_id, (blender_object, blender_curve))

		#TODO

		return (blender_object, blender_curve)

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str]:
		blender_object: bpy.types.Object = blender_resource[0]
		blender_curve: bpy.types.Curve = blender_resource[1]
		ensure_stf_id(context, blender_object.stf_instance)

		ret = {
			"type": cls.stf_type,
			"name": blender_object.stf_instance.stf_name,
		}
		ret["curve"] = context.serialize_resource(ret, blender_curve, None, STF_Category.DATA)

		#TODO

		return ret, blender_object.stf_instance.stf_id

	@classmethod
	def can_handle_blender_resource(cls, blender_resource: Any) -> int:
		if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and isinstance(blender_resource[1], bpy.types.Curve)):
			return 1000
		else:
			return -1


def register():
	pass

def unregister():
	pass
