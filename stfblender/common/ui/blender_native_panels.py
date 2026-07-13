import bpy

from .blender_native_ui import draw_blender_native_panel
from ..resource.stf_registry import find_export_handler
from ..utils.armature_bone import ArmatureBone


# TODO register a panel for all relevant bpy.types.*


class ObjectPanel(bpy.types.Panel):
	"""STF Resources for Blender Objects"""
	bl_idname = "OBJECT_PT_stf_editor_object"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"
	bl_order = -10

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "object") and context.object is not None and find_export_handler(context.object) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.object)
		draw_blender_native_panel(self.layout, context, context.object, handler) # pyright: ignore[reportArgumentType]

class ObjectInstancePanel(bpy.types.Panel):
	"""STF Resources for instantiated resources on Blender Objects"""
	bl_idname = "OBJECT_PT_stf_editor_object_instance"
	bl_label = "STF Instance Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"
	bl_order = -5

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "object") and context.object is not None and context.object.data is not None and find_export_handler((context.object, context.object.data)) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler((context.object, context.object.data))
		draw_blender_native_panel(self.layout, context, (context.object, context.object.data), handler) # pyright: ignore[reportArgumentType]

class ArmaturePanel(bpy.types.Panel):
	"""STF Resources for Blender Armatures"""
	bl_idname = "OBJECT_PT_stf_editor_armature"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"
	bl_order = -10

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "armature") and context.armature is not None and find_export_handler(context.armature) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.armature)
		draw_blender_native_panel(self.layout, context, context.armature, handler) # pyright: ignore[reportArgumentType]

class BonePanel(bpy.types.Panel):
	"""STF Resources for Blender Bones"""
	bl_idname = "OBJECT_PT_stf_editor_bone"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "bone"
	bl_order = -10

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "bone") and context.bone is not None and find_export_handler(ArmatureBone(context.armature, context.bone.name)) is not None # pyright: ignore[reportArgumentType]

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(ArmatureBone(context.armature, context.bone.name)) # pyright: ignore[reportArgumentType]
		draw_blender_native_panel(self.layout, context, ArmatureBone(context.armature, context.bone.name), handler) # pyright: ignore[reportArgumentType]

class MeshPanel(bpy.types.Panel):
	"""STF Resources for Blender Meshes"""
	bl_idname = "OBJECT_PT_stf_editor_mesh"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"
	bl_order = -10

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "mesh") and context.mesh is not None and find_export_handler(context.mesh) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.mesh)
		draw_blender_native_panel(self.layout, context, context.mesh, handler) # pyright: ignore[reportArgumentType]

class MaterialPanel(bpy.types.Panel):
	"""STF Resources for Blender Material"""
	bl_idname = "OBJECT_PT_stf_editor_material"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "material"
	bl_order = -10

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "material") and context.material is not None and find_export_handler(context.material) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.material)
		draw_blender_native_panel(self.layout, context, context.material, handler) # pyright: ignore[reportArgumentType]

class ImagePanel(bpy.types.Panel):
	"""STF Resources for Blender Images"""
	bl_idname = "OBJECT_PT_stf_editor_image"
	bl_label = "STF Editor"
	bl_region_type = "UI"
	bl_space_type = "IMAGE_EDITOR"
	bl_category = "Image"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "edit_image") and context.edit_image is not None and find_export_handler(context.edit_image) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.edit_image)
		draw_blender_native_panel(self.layout, context, context.edit_image, handler) # pyright: ignore[reportArgumentType]

class ActionPanel(bpy.types.Panel):
	"""STF Resources for Blender Actions"""
	bl_idname = "OBJECT_PT_stf_editor_action"
	bl_label = "STF Editor"
	bl_region_type = "UI"
	bl_space_type = "DOPESHEET_EDITOR"
	bl_category = "Action"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "active_action") and context.active_action is not None and find_export_handler(context.active_action) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.active_action)
		draw_blender_native_panel(self.layout, context, context.active_action, handler) # pyright: ignore[reportArgumentType]

class CameraPanel(bpy.types.Panel):
	"""STF Resources for Blender Cameras"""
	bl_idname = "OBJECT_PT_stf_editor_camera"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context) -> bool:
		return hasattr(context, "object") and context.object.data is not None and isinstance(context.object.data, bpy.types.Camera) and find_export_handler((context.object, context.object.data)) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler((context.object, context.object.data))
		draw_blender_native_panel(self.layout, context, (context.object, context.object.data), handler) # pyright: ignore[reportArgumentType]

class LightPanel(bpy.types.Panel):
	"""STF Resources for Blender Lights"""
	bl_idname = "OBJECT_PT_stf_editor_light"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context) -> bool:
		return hasattr(context, "object") and context.object.data is not None and isinstance(context.object.data, bpy.types.Light) and find_export_handler((context.object, context.object.data)) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler((context.object, context.object.data))
		draw_blender_native_panel(self.layout, context, (context.object, context.object.data), handler) # pyright: ignore[reportArgumentType]

class TextPanel(bpy.types.Panel):
	"""STF Resources for Blender Texts"""
	bl_idname = "OBJECT_PT_stf_editor_text"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.TextCurve) and find_export_handler(context.curve) is not None

	def draw(self, context: bpy.types.Context):
		handler = find_export_handler(context.curve)
		draw_blender_native_panel(self.layout, context, context.curve, handler) # pyright: ignore[reportArgumentType]
