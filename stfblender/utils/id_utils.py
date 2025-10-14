import bpy
import uuid

from .misc import CopyToClipboard
from ..base.stf_report import STFReportSeverity, STFReport


class STFSetIDOperatorBase:
	"""Set STF-ID"""
	bl_label = "Set STF-ID"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def execute(self, context):
		self.get_property(context).stf_id = str(uuid.uuid4())
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


def draw_stf_id_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_object: any, stf_prop_holder: any, set_id_op: str, is_instance: bool = False):
	layout = layout.box()
	flow = layout.split(factor=0.15)
	flow.label(text="ID:")
	if(stf_prop_holder.stf_id):
		row = flow.row(align=True)
		row_l = row.row(align=True)
		if(context.scene.stf_edit_resource_id):
			row_l.prop(stf_prop_holder, "stf_id", text="")
		else:
			row_l.label(text=stf_prop_holder.stf_id)
		row_r = row.row(align=False)
		row_r.alignment = "RIGHT"
		row_r.operator(CopyToClipboard.bl_idname, text="", icon="DUPLICATE").text = stf_prop_holder.stf_id
		row_r.prop(context.scene, "stf_edit_resource_id", text="", icon="MODIFIER")
	else:
		flow.operator(set_id_op)

	flow = layout.split(factor=0.15)
	flow.label(text="Name:")
	row = flow.row()
	if(not hasattr(stf_prop_holder, "stf_name_source_of_truth") or stf_prop_holder.stf_name_source_of_truth):
		row.prop(stf_prop_holder, "stf_name", text="")
	else:
		sub = row.row()
		sub.enabled = False
		sub.prop(blender_object, "name", text="")
	if(not is_instance):
		row_r = row.row()
		row_r.alignment = "RIGHT"
		row_r.prop(stf_prop_holder, "stf_name_source_of_truth", text="Override Name")


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


def register():
	bpy.types.Scene.stf_edit_resource_id = bpy.props.BoolProperty(name="Edit ID", description="Toggle the editing of the ID", default=False)

def unregister():
	if hasattr(bpy.types.Scene, "stf_edit_resource_id"):
		del bpy.types.Scene.stf_edit_resource_id

