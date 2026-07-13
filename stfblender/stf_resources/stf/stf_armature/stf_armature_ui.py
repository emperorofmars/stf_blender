import bpy

from .....stfblender_common.resource import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFSetArmatureIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Armature"""
	bl_idname = "stf.set_armature_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "armature") and context.armature is not None
	def get_property(self, context): return context.armature.stf_info

class STFAddArmatureComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Armature"""
	bl_idname = "stf.add_armature_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "armature") and context.armature is not None
	def get_property(self, context): return context.armature

class STFRemoveArmatureComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Armature"""
	bl_idname = "stf.remove_armature_component"
	def get_property(self, context): return context.armature

class STFEditArmatureComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_armature_component_id"
	def get_property(self, context): return context.armature

