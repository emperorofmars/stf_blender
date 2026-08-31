import bpy

from ...stfblender_common import STF_Category, stf_registry
from ...stfblender_common.utils.armature_bone import ArmatureBone
from .blender_native_ui import draw_blender_native_panel, draw_blender_native_resource_selector


# TODO register a panel for all relevant bpy.types.*
# Feel free to create a new issue or PR if you need a panel on a resource that isn't handled yet!


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
		return hasattr(context, "object") and context.object is not None and len(stf_registry.find_eligible_export_handlers(context.object)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.object, context.object.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "object") and context.object is not None and context.object.stf_info.determine_type != "none" and len(stf_registry.find_eligible_export_handlers(context.object)) > 0

	def draw(self, context: bpy.types.Context):
		context_resource = None
		if(context.object.stf_instance.determine_type == "fallback"):
			context_resource = (context.object, context.object.stf_json_fallback_instance)
		elif(context.object.data is not None):
			context_resource = (context.object, context.object.data)
		if(context_resource):
			handler = draw_blender_native_resource_selector(self.layout, context, context_resource, context.object.stf_instance) # pyright: ignore[reportArgumentType]
			if(context.object.stf_instance.determine_type == "fallback"):
				self.layout.separator(factor=1, type="SPACE")
				draw_blender_native_panel(self.layout, context, context_resource, stf_registry.get_fallback_handler(STF_Category.INSTANCE)) # pyright: ignore[reportArgumentType]
			elif(handler):
				self.layout.separator(factor=1, type="SPACE")
				draw_blender_native_panel(self.layout, context, context_resource, handler) # pyright: ignore[reportArgumentType]

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
		return hasattr(context, "armature") and context.armature is not None and len(stf_registry.find_eligible_export_handlers(context.armature)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.armature, context.armature.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "armature") and context.armature is not None and hasattr(context, "bone") and context.bone is not None and len(stf_registry.find_eligible_export_handlers(ArmatureBone(context.armature, context.bone.name))) > 0

	def draw(self, context: bpy.types.Context):
		armature_bone = ArmatureBone(context.armature, context.bone.name) # pyright: ignore[reportArgumentType]
		if(handler := draw_blender_native_resource_selector(self.layout, context, armature_bone, context.bone.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
			draw_blender_native_panel(self.layout, context, armature_bone, handler) # pyright: ignore[reportArgumentType]

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
		return hasattr(context, "mesh") and context.mesh is not None and len(stf_registry.find_eligible_export_handlers(context.mesh)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.mesh, context.mesh.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "material") and context.material is not None and len(stf_registry.find_eligible_export_handlers(context.material)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.material, context.material.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "edit_image") and context.edit_image is not None and len(stf_registry.find_eligible_export_handlers(context.edit_image)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.edit_image, context.edit_image.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "active_action") and context.active_action is not None and len(stf_registry.find_eligible_export_handlers(context.active_action)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.active_action, context.active_action.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "object") and context.object.data is not None and isinstance(context.object.data, bpy.types.Camera) and len(stf_registry.find_eligible_export_handlers((context.object, context.object.data))) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, (context.object, context.object.data), context.object.stf_instance)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
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
		return hasattr(context, "object") and context.object.data is not None and isinstance(context.object.data, bpy.types.Light) and len(stf_registry.find_eligible_export_handlers((context.object, context.object.data))) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, (context.object, context.object.data), context.object.stf_instance)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
			draw_blender_native_panel(self.layout, context, (context.object, context.object.data), handler) # pyright: ignore[reportArgumentType]

class CurvePanel(bpy.types.Panel):
	"""STF Resources for Blender Curves"""
	bl_idname = "OBJECT_PT_stf_editor_curve"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "curve") and context.curve is not None and not isinstance(context.curve, bpy.types.TextCurve) and len(stf_registry.find_eligible_export_handlers(context.curve)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.curve, context.curve.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
			draw_blender_native_panel(self.layout, context, context.curve, handler) # pyright: ignore[reportArgumentType]

class TextPanel(bpy.types.Panel):
	"""STF Resources for Blender Texts"""
	bl_idname = "OBJECT_PT_stf_editor_text"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "curve") and context.curve is not None and isinstance(context.curve, bpy.types.TextCurve) and len(stf_registry.find_eligible_export_handlers(context.curve)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.curve, context.curve.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
			draw_blender_native_panel(self.layout, context, context.curve, handler) # pyright: ignore[reportArgumentType]

class LatticePanel(bpy.types.Panel):
	"""STF Resources for Blender Lattices"""
	bl_idname = "OBJECT_PT_stf_editor_lattice"
	bl_label = "STF Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "data"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "lattice") and context.lattice is not None and len(stf_registry.find_eligible_export_handlers(context.lattice)) > 0

	def draw(self, context: bpy.types.Context):
		if(handler := draw_blender_native_resource_selector(self.layout, context, context.lattice, context.lattice.stf_info)): # pyright: ignore[reportArgumentType]
			self.layout.separator(factor=1, type="SPACE")
			draw_blender_native_panel(self.layout, context, context.lattice, handler) # pyright: ignore[reportArgumentType]
