import bpy
import uuid
from typing import Any


class STFSetIDOperatorBase:
	"""Set STF-ID"""
	bl_label = "Set STF-ID"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	def execute(self, context) -> set:
		self.get_property(context).stf_id = str(uuid.uuid4())
		return {"FINISHED"}

	def get_property(self, context) -> Any:
		pass
