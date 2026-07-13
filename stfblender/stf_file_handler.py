import bpy
from bpy_extras.io_utils import poll_file_object_drop

from .io import ExportSTF
from .io import ImportSTF


class IO_FH_stf(bpy.types.FileHandler):
	bl_idname = "IO_FH_stf"
	bl_label = "STF (.stf)"
	bl_import_operator = ImportSTF.bl_idname
	bl_export_operator = ExportSTF.bl_idname
	bl_file_extensions = ".stf"

	@classmethod
	def poll_drop(cls, context: bpy.types.Context) -> bool:
		return poll_file_object_drop(context)


def register():
	bpy.utils.register_class(IO_FH_stf)

def unregister():
	bpy.utils.unregister_class(IO_FH_stf)
