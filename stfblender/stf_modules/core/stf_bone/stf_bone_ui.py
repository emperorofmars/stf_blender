import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import draw_components_ui, set_stf_component_filter


class STFSetBoneIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Bone"""
	bl_idname = "stf.set_bone_stf_id"
	@classmethod
	def poll(cls, context): return context.bone is not None
	def get_property(self, context): return context.bone.stf_info

class STFAddBoneComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Bone"""
	bl_idname = "stf.add_bone_component"
	@classmethod
	def poll(cls, context): return context.bone is not None
	def get_property(self, context): return context.bone

class STFRemoveBoneComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Bone"""
	bl_idname = "stf.remove_bone_component"
	def get_property(self, context): return context.bone

class STFEditBoneComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_bone_component_id"
	def get_property(self, context): return context.bone


class STFBoneSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_bone_spatial_editor"
	bl_label = "STF Editor: stf.bone"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "bone"

	@classmethod
	def poll(cls, context):
		return (context.bone is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Bone)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.bone, context.bone.stf_info, STFSetBoneIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		self.layout.separator(factor=1, type="SPACE")
		header, body = self.layout.panel("stf.bone_components", default_closed = False)
		header.label(text="STF Components (" + str(len(context.bone.stf_info.stf_components)) + ")", icon="GROUP")
		if(body): draw_components_ui(self.layout, context, context.bone.stf_info, context.bone, STFAddBoneComponentOperator.bl_idname, STFRemoveBoneComponentOperator.bl_idname, STFEditBoneComponentIdOperator.bl_idname)
