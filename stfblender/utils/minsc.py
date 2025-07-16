import bpy

from .op_utils import OpenWebpage


def draw_slot_link_warning(layout: bpy.types.UILayout):
	layout.separator(factor=1, type="SPACE")
	box = layout.box()
	box.label(text="Note: The 'Slot Link' extension is required to import & export animations!")
	box.operator(OpenWebpage.bl_idname).url = "https://extensions.blender.org/add-ons/slot-link/"
	layout.separator(factor=1, type="SPACE")

