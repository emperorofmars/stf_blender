import bpy

from ....utils.data_resource_ui import draw_data_resources_ui


class STFDataResourcesCollectionPanel(bpy.types.Panel):
	bl_idname = "COLLECTION_PT_stf_data_resources_collection_editor"
	bl_label = "STF Data Resources"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "collection"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.collection is not None)

	def draw(self, context: bpy.types.Context):
		draw_data_resources_ui(self.layout, context, context.collection)


class STFDataResourcesSceneCollectionPanel(bpy.types.Panel):
	bl_idname = "COLLECTION_PT_stf_data_resources_scene_collection_editor"
	bl_label = "STF Data Resources"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "scene"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.scene is not None)

	def draw(self, context: bpy.types.Context):
		draw_data_resources_ui(self.layout, context, context.scene.collection)
