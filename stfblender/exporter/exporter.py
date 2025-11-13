import bpy
from bpy_extras.io_utils import ExportHelper

from ..base.stf_meta import draw_meta_editor
from ..base.stf_report import STFException, STFReport, STFReportSeverity
from ..base.stf_registry import get_export_modules
from .stf_export_state import STF_ExportState
from .stf_export_context import STF_ExportContext
from ..utils.misc import OpenWebpage, draw_slot_link_warning, get_stf_version
from .export_settings import STF_ExportSettings


class STF_Export_Result:
	def __init__(self, success: bool, error_message: str = None, warnings: list[STFReport] = [], export_time: float = -1):
		self.success = success
		self.error_message = error_message
		self.export_time = export_time
		self.warnings = warnings

def export_stf_file(collection: bpy.types.Collection, filepath: str, export_settings: STF_ExportSettings, debug: bool = False) -> STF_Export_Result:
	import time
	time_start = time.time()
	files = []
	trash_objects: list[bpy.types.Object] = []
	try:
		stf_state = STF_ExportState(collection.stf_meta.to_stf_meta_assetInfo(), get_export_modules(), trash_objects, settings = export_settings)
		stf_context = STF_ExportContext(stf_state)
		root_id = stf_context.serialize_resource(collection)
		stf_state.set_root_id(root_id)
		stf_state.run_tasks()

		if(not stf_state.get_root_id() and type(stf_state.get_root_id()) is not str):
			print("\nExport Failed, invalid root ID:\n\n" + str(stf_state.get_root_id()))
			raise Exception("Export Failed, invalid root ID")

		export_filepath: str = filepath
		if(not export_filepath.endswith(".stf")):
			export_filepath += ".stf"

		# Create and write stf_file to disk
		stf_file = stf_state.create_stf_binary_file()
		files.append(open(export_filepath, "wb"))
		stf_file.serialize(files[len(files) - 1])

		if(debug):
			# Write out the json itself for debugging purposes
			import json
			json_string = json.dumps(stf_file.definition.to_dict(), indent="\t").encode(encoding="utf-8")
			files.append(open(export_filepath + ".json", "wb"))
			files[len(files) - 1].write(json_string)
		return STF_Export_Result(True, warnings=stf_state._reports, export_time=time.time() - time_start)
	except STFException as error:
		print(error)
		return STF_Export_Result(False, error_message=str(error))
	except Exception as error:
		print(error)
		return STF_Export_Result(False, error_message=str(error))
	finally:
		for file in files:
			if(file is not None and not file.closed): file.close()
		for trash in trash_objects:
			if(trash is not None):
				bpy.data.objects.remove(trash)


class ExportSTF(bpy.types.Operator, ExportHelper):
	"""Export as STF file (.stf)"""
	bl_idname = "stf.export"
	bl_label = "Export STF"
	bl_options = {"PRESET", "BLOCKING"}

	filename_ext = ""
	filter_glob: bpy.props.StringProperty(default="*.stf") # type: ignore

	current_collection_as_root: bpy.props.BoolProperty(default=False, name="Scene Collection as Export Root") # type: ignore
	scene_collection_as_root: bpy.props.BoolProperty(default=False, name="Current Collection as Export Root") # type: ignore

	export_settings: bpy.props.PointerProperty(type=STF_ExportSettings) # type: ignore

	debug: bpy.props.BoolProperty(name="Export Debug Json File", default=True, description="Useful for inspection the exported file in a text-editor") # type: ignore


	def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
		if(self.scene_collection_as_root):
			context.scene.stf_collection_selector = None
		elif(self.current_collection_as_root):
			context.scene.stf_collection_selector = context.collection
		elif(context.scene.stf_root_collection):
			context.scene.stf_collection_selector = context.scene.stf_root_collection

		return ExportHelper.invoke(self, context, event)


	def execute(self, context: bpy.types.Context):
		context.window.cursor_modal_set("WAIT")
		called_from_collection_exporter = not context.space_data or context.space_data.type != "FILE_BROWSER"
		try:
			# let collection
			if(called_from_collection_exporter): # Invoked as Collection Exporter
				collection = context.collection
			else:
				collection = context.scene.stf_collection_selector if context.scene.stf_collection_selector else context.scene.collection

			export_filepath = self.filepath
			if(not export_filepath.endswith(".stf")):
				export_filepath += ".stf"

			ret = export_stf_file(collection, export_filepath, self.export_settings, self.debug)
			if(ret.success):
				do_report = False
				if(len(ret.warnings) > 0):
					for report in ret.warnings:
						if(report.severity.value >= STFReportSeverity.Warn.value):
							do_report = True
							break
				if(do_report):
					result_str = "STF asset \"" + export_filepath + "\" exported with reports! (%.3f sec.)" % ret.export_time
					self.report({"WARNING"}, result_str)
					print(result_str)
				else:
					result_str = "STF asset \"" + export_filepath + "\" exported successfully! (%.3f sec.)" % ret.export_time
					self.report({"INFO"}, result_str)
					print(result_str)
				for report in ret.warnings:
					if(report.severity.value >= STFReportSeverity.Warn.value):
						self.report({"WARNING"}, report.to_string())
					if(report.severity.value >= STFReportSeverity.Info.value):
						print(report.to_string() + "\n")
				return {"FINISHED"}
			else:
				self.report({"ERROR"}, export_filepath + " :: " + ret.error_message)
				return {"CANCELLED"}
		finally:
			context.window.cursor_modal_restore()


	def draw(self, context: bpy.types.Context):
		called_from_collection_exporter = not context.space_data or context.space_data.type != "FILE_BROWSER" # Invoked as Collection Exporter
		if(called_from_collection_exporter):
			self.layout.use_property_split = True

		if(not called_from_collection_exporter):
			self.layout.operator(OpenWebpage.bl_idname, text="Open User Guide", icon="HELP").url = "https://docs.stfform.at/guide/blender.html"
			self.layout.label(text="STF version: " + get_stf_version())
			self.layout.separator(factor=1, type="SPACE")

		draw_slot_link_warning(self.layout)

		if(not called_from_collection_exporter):
			self.layout.prop_search(bpy.context.scene, "stf_collection_selector", bpy.data, "collections", text="Root")
			if(bpy.context.scene.stf_collection_selector):
				self.layout.label(text="Remove Collection to export the entire Scene", icon="INFO")
			else:
				self.layout.label(text="Exporting full Scene", icon="INFO")

			self.layout.separator(factor=2, type="LINE")

		self.layout.prop(self, property="debug")

		self.layout.separator(factor=2, type="LINE")
		box = self.layout.box()
		box.label(text="Asset Meta")
		if(called_from_collection_exporter):
			draw_meta_editor(box, context.collection, False)
		else:
			draw_meta_editor(box, context.scene.stf_collection_selector if context.scene.stf_collection_selector else context.scene.collection, context.scene.stf_collection_selector != context.scene.collection)

		self.layout.separator(factor=2, type="LINE")
		
		self.layout.prop(self.export_settings, property="stf_mesh_vertex_colors")
		self.layout.prop(self.export_settings, property="stf_mesh_blendshape_normals")


def export_button(self, context: bpy.types.Context):
	self.layout.operator(ExportSTF.bl_idname, text="STF (.stf)")


def __poll_collection(self, object) -> bool:
	return object.stf_use_collection_as_prefab

def register():
	bpy.types.TOPBAR_MT_file_export.append(export_button)

	bpy.types.Scene.stf_collection_selector = bpy.props.PointerProperty(type=bpy.types.Collection, poll=__poll_collection, name="Collection", options={"SKIP_SAVE"}, description="Select a Collection for export") # type: ignore

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(export_button)

	if hasattr(bpy.types.Scene, "stf_collection_selector"):
		del bpy.types.Scene.stf_collection_selector
