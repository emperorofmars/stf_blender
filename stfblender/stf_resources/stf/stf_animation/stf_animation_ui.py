import bpy

from .....stfblender_common import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from .....stfblender_common.helpers import draw_slot_link_warning
from .stf_animation_bake import STFBakeAnimationOperator


class STFSetAnimationIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Animation"""
	bl_idname = "stf.set_animation_stf_id"
	@classmethod
	def poll(cls, context): return context.active_action is not None
	def get_property(self, context): return hasattr(context, "active_action") and context.active_action.stf_info

class STFAddAnimationComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Animation"""
	bl_idname = "stf.add_animation_component"
	@classmethod
	def poll(cls, context): return context.active_action is not None
	def get_property(self, context): return hasattr(context, "active_action") and context.active_action

class STFRemoveAnimationComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Animation"""
	bl_idname = "stf.remove_animation_component"
	def get_property(self, context): return hasattr(context, "active_action") and context.active_action

class STFEditAnimationComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_animation_component_id"
	def get_property(self, context): return hasattr(context, "active_action") and context.active_action


def draw_animation_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: tuple[bpy.types.Object, bpy.types.Mesh]) -> None:
	layout.use_property_split = True

	if(not hasattr(bpy.types.Action, "slot_link")):
		draw_slot_link_warning(layout)
		return

	if(context.active_action.stf_animation.is_baked_from):
		row_readonly =  layout.row()
		row_readonly.enabled = False
		row_readonly.prop(context.active_action.stf_animation, "is_baked_from")

	layout.prop(context.active_action.stf_animation, "exclude")
	if(context.active_action.stf_animation.exclude):
		return

	if(not context.active_action.stf_animation.is_baked_from):
		layout.separator(factor=2, type="SPACE")

		layout.prop(context.active_action.stf_animation, "constraint_bake")
		if(context.active_action.stf_animation.constraint_bake != "nobake"):
			layout.operator(STFBakeAnimationOperator.bl_idname)
