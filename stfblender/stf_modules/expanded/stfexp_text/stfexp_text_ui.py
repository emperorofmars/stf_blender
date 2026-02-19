import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import draw_components_ui, set_stf_component_filter


class STFSetTextIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Text"""
	bl_idname = "stf.set_text_stf_id"
	@classmethod
	def poll(cls, context): return context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)
	def get_property(self, context): return context.curve.stf_info

class STFAddTextComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Text"""
	bl_idname = "stf.add_text_component"
	@classmethod
	def poll(cls, context): return context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)
	def get_property(self, context): return context.curve

class STFRemoveTextComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Text"""
	bl_idname = "stf.remove_text_component"
	def get_property(self, context): return context.curve

class STFEditTextComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_text_component_id"
	def get_property(self, context): return context.curve


class STFTextSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_text_editor"
	bl_label = "STF Editor: stf.text"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return context.curve is not None and isinstance(context.curve, bpy.types.TextCurve)

	def draw(self, context: bpy.types.Context):
		layout = self.layout
		set_stf_component_filter(bpy.types.TextCurve)

		# Set ID
		draw_stf_id_ui(layout, context, context.curve, context.curve.stf_info, STFSetTextIDOperator.bl_idname)

		layout.separator(factor=1, type="SPACE")

		# Components
		layout.separator(factor=2, type="LINE")
		header, body = layout.panel("stf.text_components", default_closed = False)
		header.label(text="STF Components (" + str(len(context.curve.stf_info.stf_components)) + ")", icon="GROUP")
		if(body): draw_components_ui(layout, context, context.curve.stf_info, context.curve, STFAddTextComponentOperator.bl_idname, STFRemoveTextComponentOperator.bl_idname, STFEditTextComponentIdOperator.bl_idname)
