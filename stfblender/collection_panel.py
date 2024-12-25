import bpy

class STFCollectionPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_collection_editor"
	bl_label = "STF Collection Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "collection"

	def draw_header(self, context):
		pass

	def draw(self, context):
		from .export.exporter import ExportSTF
		if(context.collection.stf_id):
			self.layout.label(text="STF ID: " + context.collection.stf_id)
			# also allow editing the ID
		else:
			self.layout.label(text="Generate STF ID")

		if(context.scene.stf_root_collection == context.collection):
			self.layout.label(text="STF root prefab")
			self.layout.label(text="Export")
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF").root_collection = context.collection.name
		else:
			self.layout.label(text="Mark as STF root prefab")
			self.layout.label(text="Export")
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export this Collection as STF root prefab").root_collection = context.collection.name
