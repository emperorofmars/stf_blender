import bpy

from ..lib_stfblender.helpers.misc import CopyToClipboard as ICopyToClipboard, SetActiveObjectOperator as ISetActiveObjectOperator, OpenWebpage as IOpenWebpage


class SetActiveObjectOperator(bpy.types.Operator):
	"""Select the specified Object in the Scene"""
	bl_idname = ISetActiveObjectOperator.bl_idname
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
	"""Open in Webbrowser"""
	bl_idname = IOpenWebpage.bl_idname
	bl_label = "Open Webpage"

	url: bpy.props.StringProperty(name = "URL") # type: ignore

	def execute(self, context):
		import webbrowser
		webbrowser.open(self.url)
		return {"FINISHED"}


class CopyToClipboard(bpy.types.Operator):
	"""Copy to Clipboard"""
	bl_idname = ICopyToClipboard.bl_idname
	bl_label = "Copy to Clipboard"
	bl_options = {"REGISTER", "UNDO"}

	text: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		bpy.context.window_manager.clipboard = self.text
		return {"FINISHED"}
