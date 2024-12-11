import bpy

from ..libstf.stf_exception import STFException
from bpy_extras.io_utils import ImportHelper


class ImportSTF(bpy.types.Operator, ImportHelper):
	"""Import a STF file"""
	bl_idname = 'stf.import'
	bl_label = 'Import STF'
	bl_options = {'PRESET', 'REGISTER', 'UNDO'}
	bl_category = "STF"

	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json", options={'HIDDEN'}) # type: ignore

	def invoke(self, context, event):
		return ImportHelper.invoke_popup(self, context)

	def execute(self, context):
		try:
			print("Import")

			self.report({'INFO'}, "STF asset imported successfully!")
			return {'FINISHED'}
		except STFException as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}


def import_button(self, context):
    self.layout.operator(ImportSTF.bl_idname, text="STF (.stf/.stf.json)")

def register():
	bpy.types.TOPBAR_MT_file_import.append(import_button)

def unregister():
	bpy.types.TOPBAR_MT_file_import.remove(import_button)
