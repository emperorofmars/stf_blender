import bpy
from bpy_extras import anim_utils


def bake_constraints(action: bpy.types.Action) -> bpy.types.Action:
	ret = bpy.data.actions.new(action.name + "_baked")
	ret.stf_animation.is_baked_from = action

	animation_range = [int(action.frame_start), int(action.frame_end)] if action.use_frame_range else [int(action.frame_range[0]), int(action.frame_range[1])]

	for slotlink in action.slot_link.links:
		if(slotlink.target and type(slotlink.target) == bpy.types.Object):
			if(not slotlink.target.animation_data):
				slotlink.target.animation_data_create()
			original_action = slotlink.target.animation_data.action
			original_slot = slotlink.target.animation_data.action_slot_handle

			slotlink.target.animation_data.action = action

			anim_utils.bake_action(slotlink.target, action=ret, frames=range(animation_range[0], animation_range[1]), bake_options=anim_utils.BakeOptions(
				only_selected=False,
				do_pose=True,
				do_object=True,
				do_visual_keying=True,
				do_constraint_clear=False,
				do_parents_clear=False,
				do_clean=True,
				do_location=True,
				do_rotation=True,
				do_scale=True,
				do_bbone=True,
				do_custom_props=True
			))

			for slot in ret.slots:
				for ret_slotlink in ret.slot_link.links:
					if(slot.handle == ret_slotlink.slot_handle):
						break
				else:
					new_slotlink = ret.slot_link.links.add()
					new_slotlink.slot_handle = slot.handle
					new_slotlink.target = slotlink.target

			slotlink.target.animation_data.action = original_action
			slotlink.target.animation_data.action_slot_handle = original_slot

			# todo reset

	return ret


class STFBakeAnimationOperator(bpy.types.Operator):
	bl_idname = "stf.bake_animation"
	bl_label = "Bake Animation"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.active_action is not None and context.active_action.stf_animation.constraint_bake != "nobake")

	def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context: bpy.types.Context):
		bake_constraints(context.active_action)
		return {"FINISHED"}


class STFBakeAnimationByNameOperator(bpy.types.Operator):
	bl_idname = "stf.bake_animation_by_name"
	bl_label = "Bake Animation"
	bl_options = {"REGISTER", "UNDO", "INTERNAL"}

	action: bpy.props.StringProperty(default="") # type: ignore

	def execute(self, context: bpy.types.Context):
		if(self.action not in bpy.data.actions):
			self.report({"ERROR"}, "No Action named \"" + self.action + "\" exists!")
			return {"CANCELLED"}

		bake_constraints(bpy.data.actions[self.action])
		return {"FINISHED"}
