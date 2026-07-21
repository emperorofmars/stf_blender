import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STFReportSeverity, STFReport, STF_Category, STF_Handler_BlenderNative, STFSetIDOperatorBase, ensure_stf_id

# TODO this module is at a bare minimum level, improve it

_stf_type = "stfexp.instance.text"


class STFSetSTFEXPInstanceTextIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Text Instance"""
	bl_idname = "stf.set_stfexp_instance_text_stf_id"
	@classmethod
	def poll(cls, context) -> bool: return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.TextCurve)  # pyright: ignore[reportReturnType]
	def get_property(self, context): return context.object.stf_instance


class Handler_STFEXP_Instance_Text(STF_Handler_BlenderNative):
	stf_type = _stf_type
	stf_category = STF_Category.INSTANCE
	like_types = ["instance.text"]
	understood_blender_types = [tuple]
	operator_set_stf_id = STFSetSTFEXPInstanceTextIDOperator.bl_idname
	get_stf_prop_holder = lambda blender_resource: blender_resource[0].stf_instance

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		blender_text = context.import_resource(json_resource, json_resource["text"], STF_Category.DATA)

		blender_object = bpy.data.objects.new(json_resource.get("name", "STFEXP Instance Text"), blender_text)
		blender_object.stf_instance.stf_id = stf_id
		if(json_resource.get("name")):
			blender_object.stf_instance.stf_name = json_resource["name"]
		context.register_imported_resource(stf_id, (blender_object, blender_text))

		if(not blender_object or type(blender_object) is not bpy.types.Object):
			context.report(STFReport("Failed to import text", STFReportSeverity.Error, stf_id, _stf_type, context_resource))

		# todo handle materials

		return blender_object

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str]:
		blender_object: bpy.types.Object = blender_resource[0]
		blender_text: bpy.types.Text = blender_resource[1]
		ensure_stf_id(context, blender_object.stf_instance)

		ret = {
			"type": _stf_type,
			"name": blender_object.stf_instance.stf_name,
		}
		ret["text"] = context.serialize_resource(ret, blender_text, None, STF_Category.DATA)

		# todo handle materials

		return ret, blender_object.stf_instance.stf_id

	@staticmethod
	def can_handle_blender_resource(blender_resource: Any) -> int:
		if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and isinstance(blender_resource[1], bpy.types.TextCurve)):
			return 1000
		else:
			return -1


def register():
	pass

def unregister():
	pass
