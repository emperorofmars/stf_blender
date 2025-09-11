import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter


class STFSetImageIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Image"""
	bl_idname = "stf.set_image_stf_id"
	@classmethod
	def poll(cls, context): return context.edit_image is not None
	def get_property(self, context): return context.edit_image.stf_info


class STFAddImageComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Image"""
	bl_idname = "stf.add_image_component"
	@classmethod
	def poll(cls, context): return context.edit_image is not None
	def get_property(self, context): return context.edit_image

class STFRemoveImageComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Image"""
	bl_idname = "stf.remove_image_component"
	def get_property(self, context): return context.edit_image

class STFEditImageComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Component"""
	bl_idname = "stf.edit_image_component_id"
	def get_property(self, context): return context.edit_image


class STFImageSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_image_editor"
	bl_label = "STF Editor: stf.image"
	bl_region_type = "UI"
	bl_space_type = "IMAGE_EDITOR"
	bl_category = "Image"

	@classmethod
	def poll(cls, context):
		return (context.edit_image is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Image)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.edit_image, context.edit_image.stf_info, STFSetImageIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		self.layout.separator(factor=1, type="SPACE")
		header, body = self.layout.panel("stf.image_components", default_closed = False)
		header.label(text="STF Components", icon="GROUP")
		if(body): draw_components_ui(self.layout, context, context.edit_image.stf_info, context.edit_image, STFAddImageComponentOperator.bl_idname, STFRemoveImageComponentOperator.bl_idname, STFEditImageComponentIdOperator.bl_idname)

