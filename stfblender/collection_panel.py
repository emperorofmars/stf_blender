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
		from .exporter import ExportSTF
		if(context.collection.name.startswith("$stf_root:")):
			self.layout.label(text="STF root prefab")
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF").root_collection = context.collection.name
		else:
			self.layout.label(text="Mark as STF root prefab")
			self.layout.operator(operator=ExportSTF.bl_idname, text="Export as STF root prefab").root_collection = context.collection.name
