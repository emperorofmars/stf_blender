import bpy
import uuid

from ..utils.op_utils import CopyToClipboard
from ..core.stf_report import STFReportSeverity, STFReport


class STFSetIDOperatorBase:
	"""Set STF-ID"""
	bl_label = "Set STF-ID"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		self.get_property(context).stf_id = str(uuid.uuid4())
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_object: any, set_id_op: str, is_instance: bool = False):
	if(blender_object.stf_id):
		row = layout.row()
		row.prop(blender_object, "stf_id")
		row.operator(CopyToClipboard.bl_idname)
	else:
		layout.operator(set_id_op)

	if(not is_instance):
		layout.prop(blender_object, "stf_name_source_of_truth")

	if(blender_object.stf_name or blender_object.stf_name_source_of_truth):
		layout.prop(blender_object, "stf_name")
	else:
		layout.label(text="Using Blender Name: " + blender_object.name)


def ensure_stf_id(stf_context: any, blender_object: any):
	if(not blender_object.stf_id):
		blender_object.stf_id = str(uuid.uuid4())
	elif(stf_context.id_exists(blender_object.stf_id) and stf_context._state._permit_id_reassignment):
		original_id = blender_object.stf_id
		blender_object.stf_id = str(uuid.uuid4())
		stf_context.report(STFReport("Changed duplicate ID", STFReportSeverity.Warn, original_id, None, blender_object))
	elif(stf_context.id_exists(blender_object.stf_id) and not stf_context._state._permit_id_reassignment):
		stf_context.report(STFReport("Duplicate ID", STFReportSeverity.FatalError, blender_object.stf_id, None, blender_object))
	stf_context.register_id(blender_object, blender_object.stf_id)
