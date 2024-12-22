import json
import bpy
from bpy_extras.io_utils import ExportHelper

from ...libstf.stf_file import STF_File, STF_JsonDefinition

from .determine_export_root import determine_export_root_children, determine_export_root_collection


class ExportSTF(bpy.types.Operator, ExportHelper):
	"""Export as STF file (.stf/.stf.json)"""
	bl_idname = "stf.export"
	bl_label = "Export STF"
	bl_options = {'PRESET'}
	bl_category = "STF"

	filename_ext = ".stf"
	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json") # type: ignore

	format: bpy.props.EnumProperty(items=[("binary", "Binary", ""), ("json_contained", "Json (self contained)", ""), ("json_seperate", "Json (seperate buffers)", "")], default="binary", name="Format") # type: ignore

	root_collection: bpy.props.StringProperty(default="", name="Root Collection") # type: ignore

	debug: bpy.props.BoolProperty(name="Export Debug Json File", default=True) # type: ignore

	def invoke(self, context, event):
		if(context.scene.stf_root_collection):
			self.root_collection = context.scene.stf_root_collection.name
		return ExportHelper.invoke(self, context, event)

	def execute(self, context):
		context.window.cursor_set('WAIT')
		file = None
		file_json = None
		try:
			# Save settings if wanted

			collection = determine_export_root_collection(self.root_collection)
			determine_export_root_children(collection)

			# run modules to actually generate this definition
			json_definition = STF_JsonDefinition()

			if(self.format == "binary"):
				# Create and write stf_file to disk
				stf_file = STF_File()
				stf_file.definition = json_definition
				# set buffers
				file = open(self.filepath, "wb")
				stf_file.serialize(file)

				if(self.debug):
					# Also write out the json itself for debugging purposes
					json_string = json.dumps(json_definition.to_dict()).encode(encoding="utf-8")
					file_json = open(self.filepath + ".json", "wb")
					file_json.write(json_string)

			elif(self.format == "json_contained"):
				json_string = json.dumps(json_definition.to_dict()).encode(encoding="utf-8")
				file_json = open(self.filepath + ".stf.json", "wb")
				file_json.write(json_string)

			elif(self.format == "json_seperate"):
				json_string = json.dumps(json_definition.to_dict()).encode(encoding="utf-8")
				file_json = open(self.filepath + ".stf.json", "wb")
				file_json.write(json_string)

			self.report({'INFO'}, "STF asset exported successfully!")
			return {"FINISHED"}
		except Exception as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
		finally:
			if(file is not None and not file.closed): file.close()
			if(file_json is not None and not file_json.closed): file_json.close()
			context.window.cursor_set('DEFAULT')

	def draw(self, context):
		self.layout.prop(self, property="format")
		if(self.format == "binary"):
			self.layout.prop(self, property="debug")
		self.layout.prop(self, property="root_collection")


def export_button(self, context):
	self.layout.operator(ExportSTF.bl_idname, text="STF (.stf/.stf.json)")

def register():
	bpy.types.TOPBAR_MT_file_export.append(export_button)

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(export_button)
