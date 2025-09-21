import bpy

from ....utils.id_utils import STFSetIDOperatorBase
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import set_stf_component_filter
from .draw_prefab_ui import draw_prefab_ui


class STFSetCollectionAsRootOperator(bpy.types.Operator):
	"""Set Collection as the default STF export"""
	bl_idname = "stf.set_collection_as_export_root"
	bl_label = "Set as STF export root"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.collection is not None

	def execute(self, context):
		context.scene.stf_root_collection = context.collection
		if(not context.collection.stf_info.stf_id):
			import uuid
			context.collection.stf_info.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFSetCollectionIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Collection"""
	bl_idname = "stf.set_collection_stf_id"
	@classmethod
	def poll(cls, context): return context.collection is not None
	def get_property(self, context): return context.collection.stf_info

class STFAddCollectionComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Collection"""
	bl_idname = "stf.add_collection_component"
	@classmethod
	def poll(cls, context): return context.collection is not None
	def get_property(self, context): return context.collection

class STFRemoveCollectionComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Collection"""
	bl_idname = "stf.remove_collection_component"
	def get_property(self, context): return context.collection

class STFEditCollectionComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Component"""
	bl_idname = "stf.edit_collection_component_id"
	def get_property(self, context): return context.collection


class STFCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "COLLECTION_PT_stf_collection_editor"
	bl_label = "STF Editor: stf.prefab"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "collection"

	@classmethod
	def poll(cls, context):
		return (context.collection is not None)

	def draw_header(self, context):
		if(context.scene.stf_root_collection == context.collection):
			self.layout.label(text="Root")

	def draw(self, context):
		set_stf_component_filter(bpy.types.Collection)
		self.layout.prop(context.collection, "stf_use_collection_as_prefab")

		draw_prefab_ui(self.layout, context, context.collection, STFSetCollectionAsRootOperator.bl_idname, STFSetCollectionIDOperator.bl_idname, STFAddCollectionComponentOperator.bl_idname, STFRemoveCollectionComponentOperator.bl_idname, STFEditCollectionComponentIdOperator.bl_idname)
