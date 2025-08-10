import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter


class STFSetArmatureIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Armature"""
	bl_idname = "stf.set_armature_stf_id"
	@classmethod
	def poll(cls, context): return context.armature is not None
	def get_property(self, context): return context.armature

class STFAddArmatureComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Armature"""
	bl_idname = "stf.add_armature_component"
	@classmethod
	def poll(cls, context): return context.armature is not None
	def get_property(self, context): return context.armature

class STFRemoveArmatureComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Armature"""
	bl_idname = "stf.remove_armature_component"
	def get_property(self, context): return context.armature

class STFEditArmatureComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Component"""
	bl_idname = "stf.edit_armature_component_id"
	def get_property(self, context): return context.armature


class STFArmatureSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_armature_spatial_editor"
	bl_label = "STF Editor: stf.armature"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context):
		return (context.armature is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Armature)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.armature, context.armature.stf_info, STFSetArmatureIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.armature.stf_info, context.armature, STFAddArmatureComponentOperator.bl_idname, STFRemoveArmatureComponentOperator.bl_idname, STFEditArmatureComponentIdOperator.bl_idname)
