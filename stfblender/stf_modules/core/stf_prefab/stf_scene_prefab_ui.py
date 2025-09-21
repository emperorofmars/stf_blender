import bpy

from ....utils.id_utils import STFSetIDOperatorBase
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import set_stf_component_filter
from .draw_prefab_ui import draw_prefab_ui


class STFSetSceneCollectionAsRootOperator(bpy.types.Operator):
	"""Set Scene Collection as the default STF export"""
	bl_idname = "stf.set_scene_collection_as_export_root"
	bl_label = "Set as STF export root"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return context.scene is not None

	def execute(self, context: bpy.types.Context):
		context.scene.stf_root_collection = None
		if(not context.scene.collection.stf_info.stf_id):
			import uuid
			context.scene.collection.stf_info.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFSetSceneCollectionIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Scene Collection"""
	bl_idname = "stf.set_scene_collection_stf_id"
	@classmethod
	def poll(cls, context): return context.scene is not None
	def get_property(self, context): return context.scene.collection.stf_info

class STFAddSceneCollectionComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Scene Collection"""
	bl_idname = "stf.add_scene_collection_component"
	@classmethod
	def poll(cls, context): return context.scene.collection is not None
	def get_property(self, context): return context.scene.collection

class STFRemoveSceneCollectionComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Scene Collection"""
	bl_idname = "stf.remove_scene_collection_component"
	def get_property(self, context): return context.scene.collection

class STFEditSceneCollectionComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Component"""
	bl_idname = "stf.edit_scene_collection_component_id"
	def get_property(self, context): return context.scene.collection


class STFSceneCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "COLLECTION_PT_stf_scene_collection_editor"
	bl_label = "STF Editor: stf.prefab"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "scene"

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return (context.scene is not None)

	def draw_header(self, context: bpy.types.Context):
		if(context.scene.stf_root_collection == context.scene.collection):
			self.layout.label(text="Root")

	def draw(self, context: bpy.types.Context):
		set_stf_component_filter(bpy.types.Collection)
		self.layout.prop(context.scene.collection, "stf_use_collection_as_prefab")

		draw_prefab_ui(self.layout, context, context.scene.collection, STFSetSceneCollectionAsRootOperator.bl_idname, STFSetSceneCollectionIDOperator.bl_idname, STFAddSceneCollectionComponentOperator.bl_idname, STFRemoveSceneCollectionComponentOperator.bl_idname, STFEditSceneCollectionComponentIdOperator.bl_idname)
