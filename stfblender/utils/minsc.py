import bpy
import addon_utils

from .op_utils import OpenWebpage


def draw_slot_link_warning(layout: bpy.types.UILayout):
	if(not hasattr(bpy.types.Action, "slot_links")):
		layout.separator(factor=1, type="SPACE")
		box = layout.box()
		box.label(text="Note: The 'Slot Link' extension is required to import & export animations!")
		box.operator(OpenWebpage.bl_idname).url = "https://extensions.blender.org/add-ons/slot-link/"
		layout.separator(factor=1, type="SPACE")


def get_stf_version() -> str:
	for module in addon_utils.modules():
		if module.__name__.endswith("stf_blender"):
			version = module.bl_info.get("version", (0, 0, 0))
			return str(version[0]) + "." + str(version[1]) + "." + str(version[2])
	return "0.0.0"

