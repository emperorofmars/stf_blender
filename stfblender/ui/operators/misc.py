import bpy

from ....stfblender_common.helpers.misc import OP_CopyToClipboard, OP_OpenWebpage, OP_SetActiveObjectOperator


class SetActiveObjectOperator(bpy.types.Operator):
	"""Select the specified Object in the Scene"""
	bl_idname = OP_SetActiveObjectOperator
	bl_label = "Select"
	bl_options = {"REGISTER", "UNDO"}

	target_name: bpy.props.StringProperty(name = "target_name") # type: ignore

	def execute(self, context) -> set:
		blender_object = bpy.data.objects.get(self.target_name)
		for selected in bpy.context.selected_objects: # pyright: ignore[reportOptionalIterable]
			selected.select_set(False)
		blender_object.select_set(True)
		bpy.context.view_layer.objects.active = blender_object
		return {"FINISHED"}


class OpenWebpage(bpy.types.Operator):
	"""Open in Webbrowser"""
	bl_idname = OP_OpenWebpage
	bl_label = "Open Webpage"

	url: bpy.props.StringProperty(name = "URL") # type: ignore

	def execute(self, context) -> set:
		import webbrowser
		webbrowser.open(self.url)
		return {"FINISHED"}


class CopyToClipboard(bpy.types.Operator):
	"""Copy to Clipboard"""
	bl_idname = OP_CopyToClipboard
	bl_label = "Copy to Clipboard"
	bl_options = {"REGISTER", "UNDO"}

	text: bpy.props.StringProperty() # type: ignore

	def execute(self, context) -> set:
		bpy.context.window_manager.clipboard = self.text
		return {"FINISHED"}
