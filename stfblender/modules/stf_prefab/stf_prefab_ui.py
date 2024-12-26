import bpy


class STFSetCollectionAsRootOperator(bpy.types.Operator):
	"""Set Collection as the STF export root"""
	bl_idname = "stf.set_collection_as_export_root"
	bl_label = "Set as STF export root"
	bl_category = "STF"
	bl_context = "collection"

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
	bl_context = "collection"

	@classmethod
	def poll(cls, context):
		return context.collection is not None

	def execute(self, context):
		import uuid
		context.collection.stf_id = str(uuid.uuid4())
		return {"FINISHED"}


class STFCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_collection_editor"
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

		if(context.scene.stf_root_collection == context.collection):
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF")
		else:
			self.layout.operator(STFSetCollectionAsRootOperator.bl_idname)
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export this Collection as STF root prefab").current_collection_as_root = True

		self.layout.separator(factor=1, type="SPACE")

		if(context.collection.stf_id):
			self.layout.prop(context.collection, "stf_id")
		else:
			self.layout.operator(STFSetCollectionIDOperator.bl_idname)
