import bpy

from .dev_utils import CleanupOp, QuaternionsEverywhere, UnfuckMatrixParentInverse


def draw_dev_tools(layout: bpy.types.UILayout):
	layout.operator(CleanupOp.bl_idname)
	layout.separator(factor=1)
	layout.operator(QuaternionsEverywhere.bl_idname, icon="WARNING_LARGE")
	layout.operator(UnfuckMatrixParentInverse.bl_idname, icon="WARNING_LARGE")


class STF_Devtools(bpy.types.Panel):
	bl_idname = "OBJECT_PT_stf_devtools"
	bl_label = "STF Devtools"
	bl_region_type = "UI"
	bl_space_type = "VIEW_3D"
	bl_category = "STF"
	bl_order = 100
	bl_options = {"DEFAULT_CLOSED"}

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.scene is not None)

	def draw(self, context: bpy.types.Context):
		self.layout.use_property_split = True
		draw_dev_tools(self.layout)
