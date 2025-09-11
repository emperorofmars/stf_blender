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


def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_object: any, stf_prop_holder: any, set_id_op: str, is_instance: bool = False):
	layout = layout.box()
	if(stf_prop_holder.stf_id):
		row = layout.row(align=True)
		row.prop(stf_prop_holder, "stf_id")
		row.operator(CopyToClipboard.bl_idname, text="Copy ID").text = stf_prop_holder.stf_id
	else:
		layout.operator(set_id_op)

	row = layout.row()
	if(stf_prop_holder.stf_name_source_of_truth):
		row.prop(stf_prop_holder, "stf_name", text="Name")
	else:
		row.label(text="Name:    " + blender_object.name)
	if(not is_instance):
		row.prop(stf_prop_holder, "stf_name_source_of_truth", text="Override Name")


def ensure_stf_id(stf_context: any, blender_object: any, stf_prop_holder: any = None):
	if(not stf_prop_holder and hasattr(blender_object, "stf_info")):
		stf_prop_holder = blender_object.stf_info
	elif(not stf_prop_holder):
		stf_prop_holder = blender_object

	if(not stf_prop_holder.stf_id):
		stf_prop_holder.stf_id = str(uuid.uuid4())
	elif(stf_context.id_exists(stf_prop_holder.stf_id) and stf_context._state._permit_id_reassignment):
		original_id = stf_prop_holder.stf_id
		stf_prop_holder.stf_id = str(uuid.uuid4())
		stf_context.report(STFReport("Changed duplicate ID", STFReportSeverity.Warn, original_id, None, blender_object))
	elif(stf_context.id_exists(stf_prop_holder.stf_id) and not stf_context._state._permit_id_reassignment):
		stf_context.report(STFReport("Duplicate ID", STFReportSeverity.FatalError, stf_prop_holder.stf_id, None, blender_object))
	stf_context.register_id(blender_object, stf_prop_holder.stf_id)
