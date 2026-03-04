import bpy


class SlotLink:
	slot_handle: int
	target: bpy.types.Object
	datablock_index: int


class ActionSlotLink:
	is_reset_animation: bool
	reset_animation: bpy.types.Action
	links: list[SlotLink] # weird blender collection, use add() and remove()
	active_index: int

