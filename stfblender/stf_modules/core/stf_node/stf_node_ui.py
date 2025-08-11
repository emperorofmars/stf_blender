import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter


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


class STFNodePanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_node_editor"
	bl_label = "STF Editor: stf.node"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return (context.object is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Object)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.object, context.object.stf_info, STFSetObjectIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.object.stf_info, context.object, STFAddObjectComponentOperator.bl_idname, STFRemoveObjectComponentOperator.bl_idname, STFEditObjectComponentIdOperator.bl_idname)
