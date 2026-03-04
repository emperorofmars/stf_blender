import bpy


def poll_valid_animations(self, action: bpy.types.Action):
	return hasattr(action, "slot_link") and not action.stf_animation.exclude and len(action.slot_link.links) > 0
