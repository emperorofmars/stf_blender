import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import draw_components_ui, set_stf_component_filter


class STFSetObjectIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Object"""
	bl_idname = "stf.set_object_stf_id"
	@classmethod
	def poll(cls, context): return context.object is not None
	def get_property(self, context): return context.object.stf_info

class STFAddObjectComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Object"""
	bl_idname = "stf.add_object_component"
	@classmethod
	def poll(cls, context): return context.object is not None
	def get_property(self, context): return context.object

class STFRemoveObjectComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Object"""
	bl_idname = "stf.remove_object_component"
	def get_property(self, context): return context.object

class STFEditObjectComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Component"""
	bl_idname = "stf.edit_object_component_id"
	def get_property(self, context): return context.object


class STFNodeFixRotationMode(bpy.types.Operator):
	"""Set the rotation-mode to Quaternion"""
	bl_idname = "stf.node_fix_rotation_mode"
	bl_label = "Set the rotation-mode to Quaternion"
	bl_description = "Warning, this will break rotation-animations for this Object"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.object is not None and context.object.rotation_mode != "QUATERNION"

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event, title="Set the rotation-mode to Quaternion", message=self.bl_description)

	def execute(self, context: bpy.types.Context):
		context.object.rotation_mode = "QUATERNION"
		return {"FINISHED"}


class STFNodePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_node_editor"
	bl_label = "STF Editor: stf.node"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def draw(self, context):
		layout = self.layout
		set_stf_component_filter(bpy.types.Object)

		if(context.object.rotation_mode != "QUATERNION"):
			row = layout.row()
			row.alert = True
			row_icon = row.row()
			row_icon.alignment = "LEFT"
			row_icon.label(icon="ERROR")
			col = row.column()
			col.label(text="Please set the Rotation-Mode to 'Quaternion (WXYZ)'")
			col.label(text="Doing so ensures consistency with game-engines.")
			col.label(text="Be aware that existing rotation animations will break!")
			row_fix = col.row()
			row_fix.alignment = "LEFT"
			row_fix.operator(STFNodeFixRotationMode.bl_idname)
			layout.separator(factor=2, type="LINE")

		# Set ID
		draw_stf_id_ui(layout, context, context.object, context.object.stf_info, STFSetObjectIDOperator.bl_idname)

		layout.separator(factor=2, type="LINE")

		# Components
		layout.separator(factor=1, type="SPACE")
		header, body = layout.panel("stf.node_components", default_closed = False)
		header.label(text="STF Components", icon="GROUP")
		if(body): draw_components_ui(layout, context, context.object.stf_info, context.object, STFAddObjectComponentOperator.bl_idname, STFRemoveObjectComponentOperator.bl_idname, STFEditObjectComponentIdOperator.bl_idname)
