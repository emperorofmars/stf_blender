
import bpy
from bpy_extras.io_utils import poll_file_object_drop

class STF_File_Handler(bpy.types.FileHandler):
	bl_idname = "stf.file_handler"
	bl_label = "STF - Squirrel Transfer Format"
	bl_import_operator = "stf.import"
	bl_export_operator = "stf.export"
	bl_file_extensions = ".stf;.stf.json"
	bl_category = "STF"

	@classmethod
	def poll_drop(cls, context):
		return poll_file_object_drop(context)


from .modules import register_stf_processors
