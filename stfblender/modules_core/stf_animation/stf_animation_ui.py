import bpy

from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ...utils.component_utils import STFAddComponentOperatorBase, STFRemoveComponentOperatorBase
from ...utils.component_ui_utils import draw_components_ui, set_stf_component_filter
from .blender_slot_assignment import STFAddSlotAssignment, STFRemoveSlotAssignment


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


class STFAnimationSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_animation_spatial_editor"
	bl_label = "STF Animation Editor"
	bl_region_type = "UI"
	bl_space_type = "DOPESHEET_EDITOR"
	bl_category = "STF"
	#bl_context = "action"

	@classmethod
	def poll(cls, context):
		return (context.active_action is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Action)

		self.layout.label(text="stf.animation")

		self.layout.prop(context.active_action, "stf_exclude")
		if(context.active_action.stf_exclude):
			return

		# Set ID
		draw_stf_id_ui(self.layout, context, context.active_action, STFSetAnimationIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.active_action, STFAddAnimationComponentOperator.bl_idname, STFRemoveAnimationComponentOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Link slots to target objects to go around Blender limitations
		self.layout.label(text="In Blender, any given 'thing' can be targeted by only one Slot :(")
		self.layout.label(text="This is not how the rest of the world works.")
		self.layout.separator(factor=1, type="SPACE")
		self.layout.label(text="Assign Slots with this UI instead, until Blender fixes this limit.")
		self.layout.label(text="Using the Blender system of linking Slots to 'things' is useful for creating animations only.")
		self.layout.label(text="In a videogame context, one assignment per slot should suffice.")
		self.layout.separator(factor=1, type="SPACE")
		self.layout.label(text="Note: This workaround is jank and error-prone!")
		self.layout.label(text="Best to not ever rename slots.")
		self.layout.label(text="Good luck!")
		self.layout.separator(factor=1, type="SPACE")

		for slot_index, slot in enumerate(context.active_action.slots):
			#self.layout.separator(factor=1, type="SPACE")
			box = self.layout.box()
			box.label(text="Slot " + str(slot_index) + ": " + str(slot.name_display))

			for assignment_index, assignment in enumerate(context.active_action.stf_target_assignment):
				if(slot.name_display != assignment.slot_name):
					continue
				row = box.row()
				row.prop(assignment, "target")
				row.operator(STFRemoveSlotAssignment.bl_idname, text="", icon="X").assignment_index = assignment_index
			box.operator(STFAddSlotAssignment.bl_idname).index = slot_index


