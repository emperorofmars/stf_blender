import bpy
from bpy_extras.io_utils import poll_file_object_drop

from .exporter.exporter import ExportSTF
from .importer.importer import ImportSTF_FH, import_stf_file


class FHImportSTF(bpy.types.Operator):
	"""Import an STF file (.stf)"""
	bl_idname = "stf.fh_import"
	bl_label = "Import STF"
	bl_options = {"PRESET", "REGISTER", "UNDO"}

	filepath: bpy.props.StringProperty(subtype="FILE_PATH", options={"SKIP_SAVE"}) # type: ignore

	def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
		if self.filepath:
			return self.execute(context)
		context.window_manager.fileselect_add(self)
		return {"RUNNING_MODAL"}

	def execute(self, context: bpy.types.Context):
		if not self.filepath or not self.filepath.endswith(".stf"):
			return {"CANCELLED"}
		return import_stf_file(self, context, self.filepath)


class IO_FH_stf(bpy.types.FileHandler):
	bl_idname = "IO_FH_stf"
	bl_label = "STF (.stf)"
	bl_import_operator = ImportSTF_FH.bl_idname
	bl_export_operator = ExportSTF.bl_idname
	bl_file_extensions = ".stf"

	@classmethod
	def poll_drop(cls, context):
		return poll_file_object_drop(context)


def register():
	bpy.utils.register_class(IO_FH_stf)

def unregister():
	bpy.utils.unregister_class(IO_FH_stf)
