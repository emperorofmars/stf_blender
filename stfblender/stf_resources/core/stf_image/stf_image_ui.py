import bpy

from ....common import STFSetIDOperatorBase, STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFSetImageIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Image"""
	bl_idname = "stf.set_image_stf_id"
	@classmethod
	def poll(cls, context): return hasattr(context, "edit_image") and context.edit_image is not None
	def get_property(self, context): return context.edit_image.stf_info


class STFAddImageComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Image"""
	bl_idname = "stf.add_image_component"
	@classmethod
	def poll(cls, context): return hasattr(context, "edit_image") and context.edit_image is not None
	def get_property(self, context): return context.edit_image

class STFRemoveImageComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Image"""
	bl_idname = "stf.remove_image_component"
	def get_property(self, context): return context.edit_image

class STFEditImageComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_image_component_id"
	def get_property(self, context): return context.edit_image


class STFImageFixColorspace(bpy.types.Operator):
	"""Set the Color Space to Non-Color"""
	bl_idname = "stf.image_fix_colorspace_non_color"
	bl_label = "Fix Color Space"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context): return context.edit_image is not None

	def execute(self, context) -> set:
		context.edit_image.colorspace_settings.name = "Non-Color"
		return {"FINISHED"}


def draw_image_ui(layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: tuple[bpy.types.Object, bpy.types.Mesh]) -> None:
	layout.prop(context.edit_image.stf_image, "is_normal_map")

	if(context.edit_image.stf_image.is_normal_map and context.edit_image.colorspace_settings.name != "Non-Color"):
		warn_row = layout.row()
		warn_row.alert = True
		warn_row.label(text="Invalid Color Space!", icon="WARNING_LARGE")
		warn_row.operator(STFImageFixColorspace.bl_idname)
		layout.label(text="A Normal-Maps Color Space must be Non-Color!", icon="INFO_LARGE")
