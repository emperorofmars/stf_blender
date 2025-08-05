import bpy
import addon_utils


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


class SetActiveObjectOperator(bpy.types.Operator):
	"""Select the specified Object in the Scene"""
	bl_idname = "stf.util_set_object_active"
	bl_label = "Select"
	bl_options = {"REGISTER", "UNDO"}

	target_name: bpy.props.StringProperty(name = "target_name") # type: ignore

	def execute(self, context):
		blender_object = bpy.data.objects.get(self.target_name)
		for selected in bpy.context.selected_objects:
			selected.select_set(False)
		blender_object.select_set(True)
		bpy.context.view_layer.objects.active = blender_object
		return {"FINISHED"}


class OpenWebpage(bpy.types.Operator):
	"""Open URL in Webbrowser"""
	bl_idname = "stf.open_webpage"
	bl_label = "Open Webpage"

	url: bpy.props.StringProperty(name = "URL") # type: ignore

	def execute(self, context):
		import webbrowser
		webbrowser.open(self.url)
		return {"FINISHED"}


class CopyToClipboard(bpy.types.Operator):
	"""Copy to Clipboard"""
	bl_idname = "stf.copy_to_clipboard"
	bl_label = "Copy to Clipboard"
	bl_options = {"REGISTER", "UNDO"}

	text: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		bpy.context.window_manager.clipboard = self.text
		return {"FINISHED"}
