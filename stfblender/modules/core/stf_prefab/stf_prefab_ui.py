import bpy

from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui_utils import draw_components_ui, set_stf_component_filter
from ....stf_meta import draw_meta_editor


class STFSetCollectionAsRootOperator(bpy.types.Operator):
	"""Set Collection as the STF export root"""
	bl_idname = "stf.set_collection_as_export_root"
	bl_label = "Set as STF export root"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.collection is not None

	def execute(self, context):
		context.scene.stf_root_collection = context.collection
		if(not context.collection.stf_id):
			import uuid
			context.collection.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFSetCollectionIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Collection"""
	bl_idname = "stf.set_collection_stf_id"
	@classmethod
	def poll(cls, context): return context.collection is not None
	def get_property(self, context): return context.collection

class STFAddCollectionComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Collection"""
	bl_idname = "stf.add_collection_component"
	@classmethod
	def poll(cls, context): return context.collection is not None
	def get_property(self, context): return context.collection

class STFRemoveCollectionComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_collection_component"
	def get_property(self, context): return context.collection

class STFEditCollectionComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	bl_idname = "stf.edit_collection_component_id"
	def get_property(self, context): return context.collection


class STFCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "COLLECTION_PT_stf_collection_editor"
	bl_label = "STF Collection Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "collection"

	@classmethod
	def poll(cls, context):
		return (context.collection is not None)

	def draw_header(self, context):
		if(context.scene.stf_root_collection == context.collection):
			self.layout.label(text="Root")

	def draw(self, context):
		from ....exporter.exporter import ExportSTF
		set_stf_component_filter(bpy.types.Collection)
		self.layout.prop(context.collection, "stf_use_collection_as_prefab")

		if(context.collection.stf_use_collection_as_prefab):
			self.layout.label(text="stf.prefab")

			# Export Functionality
			if(context.scene.stf_root_collection == context.collection):
				self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF")
			else:
				self.layout.operator(STFSetCollectionAsRootOperator.bl_idname)
				self.layout.operator(operator=ExportSTF.bl_idname, text="Export this Collection as STF root prefab").current_collection_as_root = True

			self.layout.separator(factor=1, type="SPACE")

			box = self.layout.box()
			box.label(text="Asset Meta")
			draw_meta_editor(box, context.collection, False)

			self.layout.separator(factor=1, type="SPACE")

			# Set ID
			draw_stf_id_ui(self.layout, context, context.collection, STFSetCollectionIDOperator.bl_idname)

			self.layout.separator(factor=2, type="LINE")

			# Components
			draw_components_ui(self.layout, context, context.collection, STFAddCollectionComponentOperator.bl_idname, STFRemoveCollectionComponentOperator.bl_idname, STFEditCollectionComponentIdOperator.bl_idname)
