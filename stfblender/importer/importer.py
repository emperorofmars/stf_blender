import bpy
from bpy_extras.io_utils import ImportHelper

from ..core.stf_registry import get_import_modules
from .stf_import_state import STF_ImportState
from ..core.stf_report import STFException
from .stf_import_context import STF_ImportContext
from ..core.stf_file import STF_File
from ..utils.op_utils import OpenWebpage


class ImportSTF(bpy.types.Operator, ImportHelper):
	"""Import a STF file (.stf)"""
	bl_idname = 'stf.import'
	bl_label = 'Import STF'
	bl_options = {'PRESET', 'REGISTER', 'UNDO'}
	bl_category = "STF"

	filter_glob: bpy.props.StringProperty(default="*.stf", options={'HIDDEN'}) # type: ignore

	def invoke(self, context, event):
		return ImportHelper.invoke_popup(self, context)

	def execute(self, context):
		context.window.cursor_set('WAIT')
		file = None
		try:
			# Read and parse stf_file from disk
			file = open(self.filepath, "rb")
			stf_file = STF_File.parse(file)

			stf_state = STF_ImportState(stf_file, get_import_modules(bpy.context.preferences.addons.keys()))
			stf_context = STF_ImportContext(stf_state)
			root: bpy.types.Collection = stf_context.import_resource(stf_context.get_root_id(), "data")
			stf_state.run_tasks()

			if(not root or type(root) != bpy.types.Collection):
				raise Exception("Import Failed, invalid root!")

			root.stf_meta.from_stf_meta_assetInfo(stf_file.definition.stf.asset_info)

			if(len(stf_state._reports) > 0):
				self.report({'WARNING'}, "STF asset imported with reports!")
				for report in stf_state._reports:
					print(report.to_string() + "\n")
					self.report({'WARNING'}, report.to_string())
			else:
				self.report({'INFO'}, "STF asset imported successfully!")
			return {'FINISHED'}
		except STFException as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
		finally:
			if(file is not None and not file.closed): file.close()
			context.window.cursor_set('DEFAULT')

	def draw(self, context):
		self.layout.separator(factor=1, type="SPACE")

		if(not hasattr(bpy.types.Action, "slot_links")):
			self.layout.label(text="Note: the 'Slot Link' extension is")
			self.layout.label(text="required to import & export animations!")
			self.layout.operator(OpenWebpage.bl_idname).url = "https://extensions.blender.org/add-ons/slot-link/"
			self.layout.separator(factor=1, type="SPACE")


def import_button(self, context):
	self.layout.operator(ImportSTF.bl_idname, text="STF (.stf)")

def register():
	bpy.types.TOPBAR_MT_file_import.append(import_button)

def unregister():
	bpy.types.TOPBAR_MT_file_import.remove(import_button)
