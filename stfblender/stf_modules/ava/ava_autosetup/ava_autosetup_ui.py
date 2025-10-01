import bpy

from .ava_autosetup import ava_autosetup


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


# Hide in release until its more complete.

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
		self.layout.use_property_split = True
		self.layout.label(text="Automatically set-up a VR & V-Tubing avatar!")

		self.layout.prop(context.scene.ava_autosetup, "use_scene_collection")
		if(not context.scene.ava_autosetup.use_scene_collection):
			self.layout.prop(context.scene.ava_autosetup, "target_collection", text="Target", icon="OUTLINER_COLLECTION")
		
		self.layout.separator(factor=1)

		if(context.scene.ava_autosetup.use_scene_collection or context.scene.ava_autosetup.target_collection):
			self.layout.label(text="Pre-existing STF components will be removed!", icon="WARNING_LARGE")
			self.layout.operator(AVA_Autosetup_Operator.bl_idname, icon="KEY_RETURN")


def register():
	bpy.types.Scene.ava_autosetup = bpy.props.PointerProperty(type=AVA_Autosetup_Data, options=set())

def unregister():
	if hasattr(bpy.types.Scene, "ava_autosetup"):
		del bpy.types.Scene.ava_autosetup
