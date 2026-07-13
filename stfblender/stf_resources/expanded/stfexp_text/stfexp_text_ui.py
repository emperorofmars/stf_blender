import bpy

from ....common import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFSetTextIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Text"""
	bl_idname = "stf.set_text_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)
	def get_property(self, context): return context.curve.stf_info

class STFAddTextComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Text"""
	bl_idname = "stf.add_text_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)
	def get_property(self, context): return context.curve

class STFRemoveTextComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Text"""
	bl_idname = "stf.remove_text_component"
	def get_property(self, context): return context.curve

class STFEditTextComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_text_component_id"
	def get_property(self, context): return context.curve

