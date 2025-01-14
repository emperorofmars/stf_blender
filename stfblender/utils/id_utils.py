import bpy
import uuid

from ...libstf.stf_report import STFReportSeverity, STFReport


class STFSetIDOperatorBase:
	"""Set STF-ID"""
	bl_label = "Set STF-ID"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	def execute(self, context):
		self.get_property(context).stf_id = str(uuid.uuid4())
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, object: any, set_id_op: str):
	if(object.stf_id):
		layout.prop(object, "stf_id")
	else:
		layout.operator(set_id_op)


def ensure_stf_id(stf_context: any, blender_object: any):
	if(not blender_object.stf_id):
		blender_object.stf_id = str(uuid.uuid4())
	elif(stf_context.id_exists(blender_object.stf_id) and stf_context._state._permit_id_reassignment):
		original_id = blender_object.stf_id
		blender_object.stf_id = str(uuid.uuid4())
		stf_context.report(STFReport("Changed duplicate ID", STFReportSeverity.Warn, original_id, None, blender_object))
	stf_context.register_id(blender_object, blender_object.stf_id)
