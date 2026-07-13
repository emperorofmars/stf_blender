import bpy
import uuid
from typing import Any

from .. import STF_ExportContext, STFReportSeverity, STFReport


__all__ = ["STFSetIDOperatorBase", "ensure_stf_id"]


class STFSetIDOperatorBase:
	"""Set STF-ID"""
	bl_label = "Set STF-ID"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def execute(self, context) -> set:
		self.get_property(context).stf_id = str(uuid.uuid4())
		return {"FINISHED"}

	def get_property(self, context) -> Any:
		pass


def ensure_stf_id(stf_context: STF_ExportContext, blender_object: Any, stf_prop_holder: Any = None):
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

