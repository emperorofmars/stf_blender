import bpy
import uuid

from ..utils.minsc import CopyToClipboard
from ..base.stf_report import STFReportSeverity, STFReport


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
	layout = layout.box()
	if(blender_object.stf_id):
		row = layout.row(align=True)
		row.prop(blender_object, "stf_id")
		row.operator(CopyToClipboard.bl_idname, text="Copy ID")
	else:
		layout.operator(set_id_op)

	row = layout.row()
	if(blender_object.stf_name or blender_object.stf_name_source_of_truth):
		row.prop(blender_object, "stf_name", text="Name")
	else:
		row.label(text="Name: " + blender_object.name)
	if(not is_instance):
		row.prop(blender_object, "stf_name_source_of_truth", text="Override Name")


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
