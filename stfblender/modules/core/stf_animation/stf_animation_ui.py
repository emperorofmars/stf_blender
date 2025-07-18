import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter
from ....utils.minsc import draw_slot_link_warning


class STFSetAnimationIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Animation"""
	bl_idname = "stf.set_animation_stf_id"
	@classmethod
	def poll(cls, context): return context.active_action is not None
	def get_property(self, context): return context.active_action

class STFAddAnimationComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Animation"""
	bl_idname = "stf.add_animation_component"
	@classmethod
	def poll(cls, context): return context.active_action is not None
	def get_property(self, context): return context.active_action

class STFRemoveAnimationComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_animation_component"
	def get_property(self, context): return context.active_action

class STFEditAnimationComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	bl_idname = "stf.edit_animation_component_id"
	def get_property(self, context): return context.active_action


class STFAnimationSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_animation_spatial_editor"
	bl_label = "STF Editor: stf.animation"
	bl_region_type = "UI"
	bl_space_type = "DOPESHEET_EDITOR"
	bl_category = "Action"

	@classmethod
	def poll(cls, context):
		return (context.active_action is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Action)

		if(not hasattr(bpy.types.Action, "slot_links")):
			draw_slot_link_warning(self.layout)
			return

		self.layout.prop(context.active_action, "stf_exclude")
		if(context.active_action.stf_exclude):
			return

		# Set ID
		draw_stf_id_ui(self.layout, context, context.active_action, STFSetAnimationIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")
		
		self.layout.prop(context.active_action, "stf_bake")
		self.layout.label(text="Warning: Baking is destructive!")

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.active_action, STFAddAnimationComponentOperator.bl_idname, STFRemoveAnimationComponentOperator.bl_idname, STFEditAnimationComponentIdOperator.bl_idname)
