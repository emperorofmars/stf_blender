import bpy
import uuid

from ...blender_component_registry import STFAddComponentOperatorBase, STFRemoveComponentOperatorBase, draw_component, get_component_modules, draw_component_selection


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
		import uuid
		context.collection.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFSetCollectionIDOperator(bpy.types.Operator):
	"""Set STF-ID for Collection"""
	bl_idname = "stf.set_collection_stf_id"
	bl_label = "Set STF-ID"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	@classmethod
	def poll(cls, context):
		return context.collection is not None

	def execute(self, context):
		context.collection.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFAddCollectionComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Collection"""
	bl_idname = "stf.add_collection_component"

	@classmethod
	def poll(cls, context):
		return context.collection is not None

	def get_property(self, context):
		return context.collection

class STFRemoveCollectionComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_collection_component"

	def get_property(self, context):
		return context.collection



class STFDrawComponentList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


class STFCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "COLLECTION_PT_stf_collection_editor"
	bl_label = "STF Collection Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "collection"

	def draw_header(self, context):
		if(context.scene.stf_root_collection == context.collection):
			self.layout.label(text="Root")

	def draw(self, context):
		from ...export.exporter import ExportSTF

		# Export Functionality
		if(context.scene.stf_root_collection == context.collection):
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF")
		else:
			self.layout.operator(STFSetCollectionAsRootOperator.bl_idname)
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export this Collection as STF root prefab").current_collection_as_root = True

		self.layout.separator(factor=1, type="SPACE")

		# Set ID
		if(context.collection.stf_id):
			self.layout.prop(context.collection, "stf_id")
		else:
			self.layout.operator(STFSetCollectionIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		row = self.layout.row()
		draw_component_selection(row, context, "")
		row.operator(STFAddCollectionComponentOperator.bl_idname).stf_type = bpy.context.scene.stf_component_modules

		row = self.layout.row()
		row.template_list(STFDrawComponentList.bl_idname, "", context.collection, "stf_components", context.collection, "stf_active_component_index")
		if(len(context.collection.stf_components) > context.collection.stf_active_component_index):
			row.operator(STFRemoveCollectionComponentOperator.bl_idname, icon="X", text="").index = context.collection.stf_active_component_index
			draw_component(self.layout, context, context.collection.stf_components[context.collection.stf_active_component_index], context.collection)
