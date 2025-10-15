import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import draw_components_ui, set_stf_component_filter
from ....utils.misc import draw_slot_link_warning


class STFSetAnimationIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Animation"""
	bl_idname = "stf.set_animation_stf_id"
	@classmethod
	def poll(cls, context): return context.active_action is not None
	def get_property(self, context): return context.active_action.stf_info

class STFAddAnimationComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Animation"""
	bl_idname = "stf.add_animation_component"
	@classmethod
	def poll(cls, context): return context.active_action is not None
	def get_property(self, context): return context.active_action

class STFRemoveAnimationComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Animation"""
	bl_idname = "stf.remove_animation_component"
	def get_property(self, context): return context.active_action

class STFEditAnimationComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Component"""
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

		if(not hasattr(bpy.types.Action, "slot_link")):
			draw_slot_link_warning(self.layout)
			return

		self.layout.prop(context.active_action.stf_animation, "exclude")
		if(context.active_action.stf_animation.exclude):
			return

		# Set ID
		draw_stf_id_ui(self.layout, context, context.active_action, context.active_action.stf_info, STFSetAnimationIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		self.layout.separator(factor=1, type="SPACE")
		header, body = self.layout.panel("stf.animation_components", default_closed = False)
		header.label(text="STF Components", icon="GROUP")
		if(body): draw_components_ui(self.layout, context, context.active_action.stf_info, context.active_action, STFAddAnimationComponentOperator.bl_idname, STFRemoveAnimationComponentOperator.bl_idname, STFEditAnimationComponentIdOperator.bl_idname)
