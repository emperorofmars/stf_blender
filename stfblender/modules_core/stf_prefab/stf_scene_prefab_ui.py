import bpy

from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ...utils.component_utils import STFAddComponentOperatorBase, STFRemoveComponentOperatorBase
from ...utils.component_ui_utils import draw_components_ui, set_stf_component_filter
from ...stf_meta import draw_meta_editor


class STFSetSceneCollectionAsRootOperator(bpy.types.Operator):
	"""Set Scene Collection as the STF export root"""
	bl_idname = "stf.set_scene_collection_as_export_root"
	bl_label = "Set as STF export root"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.scene is not None

	def execute(self, context):
		context.scene.stf_root_collection = None
		if(not context.scene.collection.stf_id):
			import uuid
			context.scene.collection.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFSetSceneCollectionIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Scene Collection"""
	bl_idname = "stf.set_scene_collection_stf_id"
	@classmethod
	def poll(cls, context): return context.scene is not None
	def get_property(self, context): return context.scene.collection

class STFAddSceneCollectionComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Scene Collection"""
	bl_idname = "stf.add_scene_collection_component"
	@classmethod
	def poll(cls, context): return context.scene.collection is not None
	def get_property(self, context): return context.scene.collection

class STFRemoveSceneCollectionComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_scene_collection_component"
	def get_property(self, context): return context.scene.collection


class STFSceneCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "COLLECTION_PT_stf_scene_collection_editor"
	bl_label = "STF Collection Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "scene"

	@classmethod
	def poll(cls, context):
		return (context.scene is not None)

	def draw_header(self, context):
		if(context.scene.stf_root_collection == context.scene.collection):
			self.layout.label(text="Root")

	def draw(self, context):
		from ...export.exporter import ExportSTF
		set_stf_component_filter(bpy.types.Collection)
		self.layout.prop(context.scene.collection, "stf_use_collection_as_prefab")

		if(context.scene.collection.stf_use_collection_as_prefab):
			self.layout.label(text="stf.prefab")

			# Export Functionality
			if(context.scene.stf_root_collection == None):
				self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF")
			else:
				self.layout.operator(STFSetSceneCollectionAsRootOperator.bl_idname)
				self.layout.operator(operator=ExportSTF.bl_idname, text="Export this Scene as STF root prefab").scene_collection_as_root = True

			self.layout.separator(factor=1, type="SPACE")

			box = self.layout.box()
			box.label(text="Asset Meta")
			draw_meta_editor(box, context.scene.collection, True)

			self.layout.separator(factor=1, type="SPACE")

			# Set ID
			draw_stf_id_ui(self.layout, context, context.scene.collection, STFSetSceneCollectionIDOperator.bl_idname)

			self.layout.separator(factor=2, type="LINE")

			# Components
			draw_components_ui(self.layout, context, context.scene.collection, STFAddSceneCollectionComponentOperator.bl_idname, STFRemoveSceneCollectionComponentOperator.bl_idname)
