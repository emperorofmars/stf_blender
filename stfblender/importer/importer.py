import traceback
import bpy
import os
from bpy_extras.io_utils import ImportHelper

from ..base.stf_registry import get_import_modules, get_import_modules_fallback
from .stf_import_state import STF_ImportState
from ..base.stf_report import STFException, STFReport
from .stf_import_context import STF_ImportContext
from ..base.stf_file import STF_File
from ..utils.misc import OpenWebpage, draw_slot_link_warning, get_stf_version


class STF_Import_Result:
	def __init__(self, success: bool, collection: bpy.types.Collection = None, error_message: str = None, warnings: list[STFReport] = [], import_time: float = -1):
		self.success = success
		self.collection = collection
		self.error_message = error_message
		self.import_time = import_time
		self.warnings = warnings

def import_stf_file(filepath: str) -> STF_Import_Result:
	import time
	time_start = time.time()
	file = None
	trash_objects: list[bpy.types.Object] = []
	try:
		# Read and parse stf_file from disk
		file = open(filepath, "rb")
		stf_file = STF_File.parse(file)

		stf_state = STF_ImportState(stf_file, get_import_modules(), get_import_modules_fallback(), trash_objects)
		stf_context = STF_ImportContext(stf_state)
		root: bpy.types.Collection = stf_context.import_resource(stf_context.get_root_id(), "data")
		stf_state.run_tasks()

		if(not root or type(root) != bpy.types.Collection):
			raise Exception("Import Failed, invalid root!")

		root.stf_meta.from_stf_meta_assetInfo(stf_file.definition.stf.asset_info)

		return STF_Import_Result(True, collection = root, import_time=time.time() - time_start, warnings=stf_state._reports)
	except STFException as error:
		return STF_Import_Result(False, error_message=str(error))
	except Exception as error:
		return STF_Import_Result(False, error_message=str(error))
	finally:
		if(file is not None and not file.closed): file.close()
		for trash in trash_objects:
			if(trash is not None):
				bpy.data.objects.remove(trash)


class ImportSTF(bpy.types.Operator, ImportHelper):
	"""Import an STF file (.stf)"""
	bl_idname = "stf.import_files"
	bl_label = "Import STF"
	bl_options = {"PRESET", "REGISTER", "UNDO"}

	filter_glob: bpy.props.StringProperty(default="*.stf", options={"HIDDEN"}) # type: ignore

	directory: bpy.props.StringProperty(subtype="DIR_PATH") # type: ignore
	files: bpy.props.CollectionProperty(name="File Paths", type=bpy.types.OperatorFileListElement) # type: ignore


	def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
		self.invoking_from_ui = True
		return ImportHelper.invoke_popup(self, context)


	def execute(self, context: bpy.types.Context):
		context.window.cursor_modal_set("WAIT")
		try:
			result_str = ""
			total_time = 0
			total_successes = 0
			last_success = None
			for file in self.files:
				filepath = os.path.join(self.directory, file.name)
				result = import_stf_file(filepath)
				if(result.success):
					total_successes += 1
					total_time += result.import_time
					if(result.collection):
						last_success = result.collection
						result.collection.color_tag = "COLOR_07"

					if(result.warnings and len(result.warnings) > 0):
						for report in result.warnings:
							print(filepath + " :: " + report.to_string() + "\n")
							self.report({"WARNING"}, filepath + " :: " + report.to_string())

					result_str = "STF asset \"" + filepath + "\" imported successfully! (%.3f sec.)" % result.import_time
					if(len(self.files) > 1):
						print(result_str)
				else:
					self.report({"ERROR"}, filepath + " :: " + result.error_message)

			if(total_successes == len(self.files)):
				if(total_successes > 1):
					result_str = str(len(self.files)) + " STF assets imported successfully! (%.3f sec.)" % total_time
				self.report({"INFO"}, result_str)
				print(result_str)
			if(last_success):
				if(not context.scene.stf_root_collection):
					context.scene.stf_root_collection = last_success
				# Select the imported assets Collection
				bpy.context.view_layer.active_layer_collection = context.view_layer.layer_collection.children[last_success.name]
			return {"FINISHED"}
		except Exception as error:
			print(error)
			print(traceback.format_exc())
		finally:
			context.window.cursor_modal_restore()


	def draw(self, context: bpy.types.Context):
		self.layout.operator(OpenWebpage.bl_idname, text="Open User Guide", icon="HELP").url = "https://docs.stfform.at/guide/blender.html"
		self.layout.label(text="STF version: " + get_stf_version())
		self.layout.separator(factor=1, type="SPACE")

		draw_slot_link_warning(self.layout)


def import_button(self, context: bpy.types.Context):
	self.layout.operator(ImportSTF.bl_idname, text="STF (.stf)")


def register():
	bpy.types.TOPBAR_MT_file_import.append(import_button)

def unregister():
	bpy.types.TOPBAR_MT_file_import.remove(import_button)
