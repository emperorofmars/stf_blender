import bpy
from bpy_extras import anim_utils


def bake_constraints(action: bpy.types.Action) -> bpy.types.Action:
	ret = bpy.data.actions.new(action.name + "_baked")
	ret.stf_animation.is_baked_from = action
	ret.stf_animation.exclude = True
	ret.stf_animation.constraint_bake = "nobake"
	ret.use_cyclic = action.use_cyclic

	animation_range = [int(action.frame_start), int(action.frame_end)] if action.use_frame_range else [int(action.frame_range[0]), int(action.frame_range[1])]
	if(animation_range[1] <= animation_range[0]): animation_range[1] = animation_range[0] + 1

	for slotlink in action.slot_link.links:
		if(slotlink.target):
			for slot in action.slots:
				if(slot.handle == slotlink.slot_handle):
					break
			else:
				continue
			if(slot.target_id_type != "OBJECT"):
				continue

			if(not slotlink.target.animation_data):
				slotlink.target.animation_data_create()
			original_action = slotlink.target.animation_data.action
			original_slot = slotlink.target.animation_data.action_slot_handle

			slotlink.target.animation_data.action = action
			slotlink.target.animation_data.action_slot_handle = slotlink.slot_handle

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

			for ret_slot in ret.slots:
				for ret_slotlink in ret.slot_link.links:
					if(ret_slot.handle == ret_slotlink.slot_handle):
						break
				else:
					new_slotlink = ret.slot_link.links.add()
					new_slotlink.slot_handle = ret_slot.handle
					new_slotlink.target = slotlink.target
					new_slotlink.datablock_index = slotlink.datablock_index

			slotlink.target.animation_data.action = original_action
			slotlink.target.animation_data.action_slot_handle = original_slot

	bpy.context.scene.frame_set(bpy.context.scene.frame_current)

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

