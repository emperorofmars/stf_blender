import bpy
from bpy_extras.io_utils import ExportHelper

from ..base.stf_meta import draw_meta_editor
from ..base.stf_report import STFReportSeverity
from ..base.stf_registry import get_export_modules
from .stf_export_state import STF_ExportState
from .stf_export_context import STF_ExportContext
from ..utils.minsc import draw_slot_link_warning, get_stf_version
from .export_settings import STF_ExportSettings


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


	def invoke(self, context, event):
		if(self.scene_collection_as_root):
			context.scene.stf_collection_selector = None
		elif(self.current_collection_as_root):
			context.scene.stf_collection_selector = context.collection
		elif(context.scene.stf_root_collection):
			context.scene.stf_collection_selector = context.scene.stf_root_collection
		return ExportHelper.invoke(self, context, event)


	def execute(self, context):
		import time
		time_start = time.time()
		context.window.cursor_set("WAIT")
		files = []
		trash_objects: list[bpy.types.Object] = []
		try:
			collection = context.scene.stf_collection_selector if context.scene.stf_collection_selector else context.scene.collection

			stf_state = STF_ExportState(collection.stf_meta.to_stf_meta_assetInfo(), get_export_modules(), trash_objects, settings = self.export_settings)
			stf_context = STF_ExportContext(stf_state)
			root_id = stf_context.serialize_resource(collection)
			stf_state.set_root_id(root_id)
			stf_state.run_tasks()

			if(not stf_state.get_root_id() and type(stf_state.get_root_id()) is not str):
				print("\nExport Failed, invalid root ID:\n\n" + str(stf_state.get_root_id()))
				raise Exception("Export Failed, invalid root ID")

			export_filepath: str = self.filepath
			if(not export_filepath.endswith(".stf")):
				export_filepath += ".stf"

			# Create and write stf_file to disk
			stf_file = stf_state.create_stf_binary_file()
			files.append(open(export_filepath, "wb"))
			stf_file.serialize(files[len(files) - 1])

			if(self.debug):
				# Write out the json itself for debugging purposes
				import json
				json_string = json.dumps(stf_file.definition.to_dict(), indent="\t").encode(encoding="utf-8")
				files.append(open(export_filepath + ".json", "wb"))
				files[len(files) - 1].write(json_string)

			do_report = False
			if(len(stf_state._reports) > 0):
				for report in stf_state._reports:
					if(report.severity.value >= STFReportSeverity.Warn.value):
						do_report = True
						break
			if(do_report):
				self.report({"WARNING"}, "STF asset exported with reports! (%.3f sec.)" % (time.time() - time_start))
			else:
				self.report({"INFO"}, "STF asset exported successfully! (%.3f sec.)" % (time.time() - time_start))
			for report in stf_state._reports:
				if(report.severity.value >= STFReportSeverity.Warn.value):
					self.report({"WARNING"}, report.to_string())
				if(report.severity.value >= STFReportSeverity.Info.value):
					print(report.to_string() + "\n")
			return {"FINISHED"}
		finally:
			for file in files:
				if(file is not None and not file.closed): file.close()
			for trash in trash_objects:
				if(trash is not None):
					bpy.data.objects.remove(trash)
			context.window.cursor_set("DEFAULT")


	def draw(self, context):
		self.layout.label(text="STF version: " + get_stf_version())
		self.layout.separator(factor=1, type="SPACE")

		draw_slot_link_warning(self.layout)

		self.layout.prop_search(bpy.context.scene, "stf_collection_selector", bpy.data, "collections", text="Root")
		if(bpy.context.scene.stf_collection_selector):
			self.layout.label(text="Remove Collection to export the entire Scene")
		else:
			self.layout.label(text="Exporting full Scene")

		self.layout.separator(factor=2, type="LINE")

		self.layout.prop(self, property="debug")

		self.layout.separator(factor=2, type="LINE")
		box = self.layout.box()
		box.label(text="Asset Meta")
		draw_meta_editor(box, context.scene.stf_collection_selector if context.scene.stf_collection_selector else context.scene.collection, context.scene.stf_collection_selector != context.scene.collection)

		self.layout.separator(factor=2, type="LINE")
		
		self.layout.prop(self.export_settings, property="stf_mesh_vertex_colors")
		self.layout.prop(self.export_settings, property="stf_mesh_blendshape_normals")


def export_button(self, context):
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
