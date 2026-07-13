import bpy


OP_SetActiveObjectOperator = "stf.util_set_object_active"

OP_OpenWebpage = "stf.open_webpage"

OP_CopyToClipboard = "stf.copy_to_clipboard"


def draw_slot_link_warning(layout: bpy.types.UILayout):
	if(not hasattr(bpy.types.Action, "slot_link")):
		layout.separator(factor=1, type="SPACE")
		box = layout.box()
		box.label(text="Note: The 'Slot Link' extension is required to import & export animations!")
		box.operator(OP_OpenWebpage).url = "https://extensions.blender.org/add-ons/slot-link/"
		layout.separator(factor=1, type="SPACE")


def get_stf_version() -> str:
	import addon_utils
	for module in addon_utils.modules(): # pyright: ignore[reportGeneralTypeIssues]
		if module.__name__.endswith("stf_blender"):
			version = module.bl_info.get("version", (0, 0, 0))
			return str(version[0]) + "." + str(version[1]) + "." + str(version[2])
	return "0.0.0"
