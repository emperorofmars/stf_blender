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


def ensure_stf_id(context: STF_ExportContext, blender_object: Any, stf_prop_holder: Any = None) -> None:
	"""
	Sets an ID for the `blender_object` and ensures its uniqueness.

	:param STF_ExportContext context:
	:param Any blender_object: Blender-native representation of an STF resource
	:param Any stf_prop_holder: Optional object which holds the `stf_id` property for the resource. It's `stf_info` by default.
	"""
	if(not stf_prop_holder and hasattr(blender_object, "stf_info")):
		stf_prop_holder = blender_object.stf_info
	elif(not stf_prop_holder):
		stf_prop_holder = blender_object

	if(not stf_prop_holder.stf_id):
		stf_prop_holder.stf_id = str(uuid.uuid4())
	elif(context.id_exists(stf_prop_holder.stf_id) and context._state._permit_id_reassignment):
		original_id = stf_prop_holder.stf_id
		stf_prop_holder.stf_id = str(uuid.uuid4())
		context.report(STFReport("Changed duplicate ID", STFReportSeverity.Warn, original_id, None, blender_object))
	elif(context.id_exists(stf_prop_holder.stf_id) and not context._state._permit_id_reassignment):
		context.report(STFReport("Duplicate ID", STFReportSeverity.FatalError, stf_prop_holder.stf_id, None, blender_object))
	context.register_id(blender_object, stf_prop_holder.stf_id)

