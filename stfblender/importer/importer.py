import bpy
from bpy_extras.io_utils import ImportHelper

from ..base.stf_registry import get_import_modules
from .stf_import_state import STF_ImportState
from ..base.stf_report import STFException
from .stf_import_context import STF_ImportContext
from ..base.stf_file import STF_File
from ..utils.minsc import draw_slot_link_warning, get_stf_version


class ImportSTF(bpy.types.Operator, ImportHelper):
	"""Import an STF file (.stf)"""
	bl_idname = "stf.import"
	bl_label = "Import STF"
	bl_options = {"PRESET", "REGISTER", "UNDO"}

	filter_glob: bpy.props.StringProperty(default="*.stf", options={"HIDDEN"}) # type: ignore

	def invoke(self, context, event):
		return ImportHelper.invoke_popup(self, context)

	def execute(self, context):
		import time
		time_start = time.time()
		context.window.cursor_set("WAIT")
		file = None
		trash_objects: list[bpy.types.Object] = []
		try:
			# Read and parse stf_file from disk
			file = open(self.filepath, "rb")
			stf_file = STF_File.parse(file)

			stf_state = STF_ImportState(stf_file, get_import_modules(), trash_objects)
			stf_context = STF_ImportContext(stf_state)
			root: bpy.types.Collection = stf_context.import_resource(stf_context.get_root_id(), "data")
			stf_state.run_tasks()

			if(not root or type(root) != bpy.types.Collection):
				raise Exception("Import Failed, invalid root!")

			root.stf_meta.from_stf_meta_assetInfo(stf_file.definition.stf.asset_info)
			if(not context.scene.stf_root_collection):
				context.scene.stf_root_collection = root

			if(len(stf_state._reports) > 0):
				self.report({"WARNING"}, "STF asset imported with reports! (%.3f sec.)" % (time.time() - time_start))
				for report in stf_state._reports:
					print(report.to_string() + "\n")
					self.report({"WARNING"}, report.to_string())
			else:
				self.report({"INFO"}, "STF asset imported successfully! (%.3f sec.)" % (time.time() - time_start))
			return {"FINISHED"}
		except STFException as error:
			self.report({"ERROR"}, str(error))
			return {"CANCELLED"}
		finally:
			if(file is not None and not file.closed): file.close()
			for trash in trash_objects:
				if(trash is not None):
					bpy.data.objects.remove(trash)
			context.window.cursor_set("DEFAULT")

	def draw(self, context):
		self.layout.label(text="STF version: " + get_stf_version())
		self.layout.separator(factor=1, type="SPACE")

		draw_slot_link_warning(self.layout)


def import_button(self, context):
	self.layout.operator(ImportSTF.bl_idname, text="STF (.stf)")

def register():
	bpy.types.TOPBAR_MT_file_import.append(import_button)

def unregister():
	bpy.types.TOPBAR_MT_file_import.remove(import_button)
