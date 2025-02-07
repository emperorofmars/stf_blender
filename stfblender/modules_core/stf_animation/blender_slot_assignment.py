import bpy


class SlotTargetAssignment(bpy.types.PropertyGroup):
	slot_handle: bpy.props.IntProperty(name="Slot Handle", default=-1) # type: ignore
	target: bpy.props.PointerProperty(type=bpy.types.Object, name="Target") # type: ignore


class STFAddSlotAssignment(bpy.types.Operator):
	bl_idname = "stf.add_slot_assignment"
	bl_label = "Add Slot Assignment"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "Slot Index", default=-1) # type: ignore

	def execute(self, context):
		slot_assignment = context.active_action.stf_target_assignment.add()
		slot_assignment.slot_handle = context.active_action.slots[self.index].handle
		return {"FINISHED"}


class STFRemoveSlotAssignment(bpy.types.Operator):
	bl_idname = "stf.remove_slot_assignment"
	bl_label = "Remove Slot Assignment"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	assignment_index: bpy.props.IntProperty(name = "Assignment Index", default=-1) # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		context.active_action.stf_target_assignment.remove(self.assignment_index)
		return {"FINISHED"}


def register():
	bpy.types.Action.stf_target_assignment = bpy.props.CollectionProperty(type=SlotTargetAssignment, name="Assignments") # type: ignore

def unregister():
	if hasattr(bpy.types.Action, "stf_target_assignment"):
		del bpy.types.Action.stf_target_assignment
