import bpy
from typing import Protocol

__all__ = ["SlotLink", "ActionSlotLink"]

class SlotLink(Protocol):
	slot_handle: int
	target: bpy.types.Object
	datablock_index: int


class ActionSlotLink(Protocol):
	is_reset_animation: bool
	reset_animation: bpy.types.Action
	links: list[SlotLink] # weird blender collection, use add() and remove()
	active_index: int

