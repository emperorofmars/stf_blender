import bpy


def draw_slot_link_warning(layout: bpy.types.UILayout):
	if(not hasattr(bpy.types.Action, "slot_link")):
		layout.separator(factor=1, type="SPACE")
		box = layout.box()
		box.label(text="Note: The 'Slot Link' extension is required to import & export animations!")
		box.operator(OpenWebpage.bl_idname).url = "https://extensions.blender.org/add-ons/slot-link/"
		layout.separator(factor=1, type="SPACE")


def get_stf_version() -> str:
	import addon_utils
	for module in addon_utils.modules():
		if module.__name__.endswith("stf_blender"):
			version = module.bl_info.get("version", (0, 0, 0))
			return str(version[0]) + "." + str(version[1]) + "." + str(version[2])
	return "0.0.0"


class SetActiveObjectOperator:
	"""Select the specified Object in the Scene"""
	bl_idname = "stf.util_set_object_active"
	target_name: str


class OpenWebpage:
	"""Open in Webbrowser"""
	bl_idname = "stf.open_webpage"
	url: str


class CopyToClipboard:
	"""Copy to Clipboard"""
	bl_idname = "stf.copy_to_clipboard"
	text: str
