import bpy

from .....stfblender_common.resource import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFSetObjectIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Object"""
	bl_idname = "stf.set_object_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "object") and context.object is not None
	def get_property(self, context): return context.object.stf_info

class STFAddObjectComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Object"""
	bl_idname = "stf.add_object_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "object") and context.object is not None
	def get_property(self, context): return context.object

class STFRemoveObjectComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Object"""
	bl_idname = "stf.remove_object_component"
	def get_property(self, context): return context.object

class STFEditObjectComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_object_component_id"
	def get_property(self, context): return context.object


class STFNodeFixRotationMode(bpy.types.Operator):
	"""Set the rotation-mode to Quaternion"""
	bl_idname = "stf.node_fix_rotation_mode"
	bl_label = "Set the rotation-mode to Quaternion"
	bl_description = "Warning, this will break rotation-animations for this Object"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return hasattr(context, "object") and context.object is not None and context.object.rotation_mode != "QUATERNION"

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event, title="Set the rotation-mode to Quaternion", message=self.bl_description)

	def execute(self, context: bpy.types.Context) -> set:
		context.object.rotation_mode = "QUATERNION"
		return {"FINISHED"}
