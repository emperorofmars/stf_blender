import bpy

from ..libstf.stf_exception import STFException
from bpy_extras.io_utils import ExportHelper


class ExportSTF(bpy.types.Operator, ExportHelper):
	"""Export as STF file"""
	bl_idname = "stf.export"
	bl_label = "Export STF"
	bl_options = {'PRESET'}
	bl_category = "STF"

	filename_ext = ""
	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json", options={'HIDDEN'}) # type: ignore

	root_collection: bpy.props.StringProperty(default="") # type: ignore

	def invoke(self, context, event):
		return ExportHelper.invoke(self, context, event)

	def execute(self, context):
		try:
			print("export")

			# save settings of wanted

			# create stf_file

			# write stf_file to disk

			self.report({'INFO'}, "STF asset exported successfully!")
			return {"FINISHED"}
		except STFException as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def export_button(self, context):
    self.layout.operator(ExportSTF.bl_idname, text="STF (.stf/.stf.json)")

def register():
	bpy.types.TOPBAR_MT_file_export.append(export_button)

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(export_button)
