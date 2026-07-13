import bpy

from .....stfblender_common import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFSetBoneIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Bone"""
	bl_idname = "stf.set_bone_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "bone") and context.bone is not None
	def get_property(self, context): return context.bone.stf_info

class STFAddBoneComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Bone"""
	bl_idname = "stf.add_bone_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "bone") and context.bone is not None
	def get_property(self, context): return context.bone

class STFRemoveBoneComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Bone"""
	bl_idname = "stf.remove_bone_component"
	def get_property(self, context): return context.bone

class STFEditBoneComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_bone_component_id"
	def get_property(self, context): return context.bone
