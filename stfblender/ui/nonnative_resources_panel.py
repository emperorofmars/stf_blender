import bpy

from .nonnative_resource_ui import draw_data_resources_ui


class STFNonNativeResourcesCollectionPanel(bpy.types.Panel):
	bl_idname = "COLLECTION_PT_stf_nonnative_resources_collection_editor"
	bl_label = "STF Non-Native Resources"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "collection"

	@classmethod
	def poll(cls, context: bpy.types.Context) -> bool:
		return (context.collection is not None)

	def draw(self, context: bpy.types.Context):
		draw_data_resources_ui(self.layout, context, context.collection) # pyright: ignore[reportArgumentType]


class STFNonNativeResourcesSceneCollectionPanel(bpy.types.Panel):
	bl_idname = "COLLECTION_PT_stf_nonnative_resources_scene_collection_editor"
	bl_label = "STF Non-Native Resources"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "scene"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.scene is not None)

	def draw(self, context: bpy.types.Context):
		draw_data_resources_ui(self.layout, context, context.scene.collection) # pyright: ignore[reportArgumentType]
