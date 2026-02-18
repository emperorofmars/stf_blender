import bpy

from .ava_autosetup import ava_autosetup, detect_mesh_and_armature


class AVA_Autosetup_Data(bpy.types.PropertyGroup):
	use_scene_collection: bpy.props.BoolProperty(name="Use Scene Collection", default=False, options=set()) # type: ignore
	target_collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Target Collection", options=set()) # type: ignore


class AVA_Autosetup_Operator(bpy.types.Operator):
	"""Automatic setup of VR & V-Tubing avatar components"""
	bl_idname = "ava.autosetup"
	bl_label = "Autosetup"
	bl_options = {"REGISTER", "UNDO", "BLOCKING"}

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.scene is not None and context.scene.ava_autosetup.use_scene_collection or context.scene.ava_autosetup.target_collection)

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		try:
			ava_autosetup(context.scene.collection if context.scene.ava_autosetup.use_scene_collection else context.collection)
			self.report({"INFO"}, "AVA autosetup succeeded")
			return {"FINISHED"}
		except Exception as e:
			print(e)
			self.report({"ERROR"}, "AVA autosetup failed: " + str(e))
			return {"CANCELLED"}


class AVA_Autosetup_Panel(bpy.types.Panel):
	bl_idname = "OBJECT_PT_ava_autosetup"
	bl_label = "STF-AVA Autosetup"
	bl_region_type = "UI"
	bl_space_type = "VIEW_3D"
	bl_category = "STF"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.scene is not None)

	def draw(self, context: bpy.types.Context):
		layout = self.layout
		layout.label(text="Automatically set-up a VR & V-Tubing avatar!")
		layout.separator(factor=1)

		if(not context.scene.ava_autosetup.use_scene_collection):
			layout.prop(context.scene.ava_autosetup, "target_collection", text="Target", icon="OUTLINER_COLLECTION")
		if(not context.scene.ava_autosetup.target_collection):
			layout.prop(context.scene.ava_autosetup, "use_scene_collection")

		layout.separator(factor=1)

		selected_col = None
		main_mesh = None
		main_armature = None
		if(context.scene.ava_autosetup.use_scene_collection):
			selected_col = context.scene.collection
		elif(context.scene.ava_autosetup.target_collection):
			selected_col = context.scene.ava_autosetup.target_collection
		if(selected_col):
			detect_ret = detect_mesh_and_armature(selected_col)
			if(detect_ret):
				main_mesh, main_armature = detect_ret
				layout.label(text="Detected Body Mesh: " + main_mesh.name, icon="CHECKMARK")
				layout.label(text="Detected Armature: " + main_armature.name, icon="CHECKMARK")
			else:
				layout.label(text="Couldn't find Body Mesh!", icon="ERROR")
				layout.label(text="Couldn't find Armature!", icon="ERROR")

		layout.separator(factor=1)

		if(main_mesh and main_armature and context.scene.ava_autosetup.use_scene_collection or context.scene.ava_autosetup.target_collection):
			layout.label(text="Pre-existing STF components will be removed!", icon="WARNING_LARGE")
			layout.separator(factor=1)
			layout.operator(AVA_Autosetup_Operator.bl_idname, icon="KEY_RETURN")
		layout.separator(factor=1)


def register():
	bpy.types.Scene.ava_autosetup = bpy.props.PointerProperty(type=AVA_Autosetup_Data, options=set())

def unregister():
	if hasattr(bpy.types.Scene, "ava_autosetup"):
		del bpy.types.Scene.ava_autosetup
