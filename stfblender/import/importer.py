import bpy
from bpy_extras.io_utils import ImportHelper

from ...libstf.stf_report import STFException
from ...libstf.stf_import_context import STF_ImportContext
from ...libstf.stf_file import STF_File


class ImportSTF(bpy.types.Operator, ImportHelper):
	"""Import a STF file (.stf/.stf.json)"""
	bl_idname = 'stf.import'
	bl_label = 'Import STF'
	bl_options = {'PRESET', 'REGISTER', 'UNDO'}
	bl_category = "STF"

	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json", options={'HIDDEN'}) # type: ignore

	def invoke(self, context, event):
		return ImportHelper.invoke_popup(self, context)

	def execute(self, context):
		context.window.cursor_set('WAIT')
		file = None
		try:
			# Read and parse stf_file from disk
			file = open(self.filepath, "rb")
			stf_file = STF_File.parse(file)

			stf_context = STF_ImportContext(stf_file)
			root = stf_context.import_resource(stf_context.get_root_id())


			print("stf_file")
			print(root)
			print(stf_file.definition.to_dict())


			self.report({'INFO'}, "STF asset imported successfully!")
			return {'FINISHED'}
		except STFException as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
		finally:
			if(file is not None and not file.closed): file.close()
			context.window.cursor_set('DEFAULT')


def import_button(self, context):
    self.layout.operator(ImportSTF.bl_idname, text="STF (.stf/.stf.json)")

def register():
	bpy.types.TOPBAR_MT_file_import.append(import_button)

def unregister():
	bpy.types.TOPBAR_MT_file_import.remove(import_button)
