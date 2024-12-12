import json
import bpy
from bpy_extras.io_utils import ExportHelper

from ..libstf.stf_file import STF_File, STF_JsonDefinition
from ..libstf.stf_exception import STFException


class ExportSTF(bpy.types.Operator, ExportHelper):
	"""Export as STF file"""
	bl_idname = "stf.export"
	bl_label = "Export STF"
	bl_options = {'PRESET'}
	bl_category = "STF"

	filename_ext = ".stf"
	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json") # type: ignore

	root_collection: bpy.props.StringProperty(default="") # type: ignore

	def invoke(self, context, event):
		return ExportHelper.invoke(self, context, event)

	def execute(self, context):
		context.window.cursor_set('WAIT')
		file = None
		file_json = None
		try:
			# Save settings if wanted

			# Create and write stf_file to disk
			stf_file = STF_File()
			file = open(self.filepath, "wb")
			stf_file.serialize(file)

			json_string = json.dumps(stf_file.definition.to_dict()).encode(encoding="utf-8")
			file_json = open(self.filepath + ".json", "wb")
			file_json.write(json_string)

			self.report({'INFO'}, "STF asset exported successfully!")
			return {"FINISHED"}
		except STFException as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
		finally:
			if(file is not None): file.close()
			if(file_json is not None): file_json.close()
			context.window.cursor_set('DEFAULT')


def export_button(self, context):
    self.layout.operator(ExportSTF.bl_idname, text="STF (.stf/.stf.json)")

def register():
	bpy.types.TOPBAR_MT_file_export.append(export_button)

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(export_button)
