
import bpy
import uuid

from ...utils.id_utils import draw_stf_id_ui
from ...utils.component_utils import STFAddComponentOperatorBase, STFRemoveComponentOperatorBase, draw_components_ui, set_stf_component_filter


class STFSetObjectIDOperator(bpy.types.Operator):
	"""Set STF-ID for Object"""
	bl_idname = "stf.set_object_stf_id"
	bl_label = "Set STF-ID"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def execute(self, context):
		context.object.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFAddObjectComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Object"""
	bl_idname = "stf.add_object_component"

	@classmethod
	def poll(cls, context):
		return context.object is not None

	def get_property(self, context):
		return context.object


class STFRemoveObjectComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_object_component"

	def get_property(self, context):
		return context.object


class STFNodeSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_node_spatial_editor"
	bl_label = "STF Object Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "object"

	def draw(self, context):
		set_stf_component_filter(bpy.types.Object)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.object, STFSetObjectIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.object, STFAddObjectComponentOperator.bl_idname, STFRemoveObjectComponentOperator.bl_idname)
