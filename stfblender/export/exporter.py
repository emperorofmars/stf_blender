import json
import bpy
from bpy_extras.io_utils import ExportHelper

from ...libstf.stf_registry import get_stf_processors
from ...libstf.stf_report import STFException
from ...libstf.stf_definition import STF_Meta_AssetInfo
from ...libstf.stf_export_context import STF_ExportContext, create_stf_binary_file, create_stf_definition


class ExportSTF(bpy.types.Operator, ExportHelper):
	"""Export as STF file (.stf/.stf.json)"""
	bl_idname = "stf.export"
	bl_label = "Export STF"
	bl_options = {'PRESET'}
	bl_category = "STF"

	filename_ext = ""
	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json") # type: ignore

	current_collection_as_root: bpy.props.BoolProperty(default=False, name="Current Collection as Export Root") # type: ignore

	format: bpy.props.EnumProperty(items=[("binary", "Binary", ""), ("json_contained", "Json (self contained)", ""), ("json_seperate", "Json (seperate buffers)", "")], default="binary", name="Format") # type: ignore
	debug: bpy.props.BoolProperty(name="Export Debug Json File", default=True) # type: ignore

	def invoke(self, context, event):
		if(self.current_collection_as_root):
			context.scene.stf_collection_selector = context.collection
		elif(context.scene.stf_root_collection):
			context.scene.stf_collection_selector = context.scene.stf_root_collection
		return ExportHelper.invoke(self, context, event)

	def execute(self, context):
		context.window.cursor_set('WAIT')
		files = []
		try:
			collection = context.scene.stf_collection_selector if context.scene.stf_collection_selector else context.scene.collection

			processors = get_stf_processors(bpy.context.preferences.addons.keys())

			# TODO: configure profiles, generate asset info
			stf_context = STF_ExportContext(profiles=[], asset_info=STF_Meta_AssetInfo(), processors=processors)

			# run modules to actually generate this definition
			stf_context.serialize_resource(collection)

			if(not stf_context.get_root_id()):
				raise Exception("Export Failed")

			if(self.format == "binary"):
				export_filepath: str = self.filepath
				if(not export_filepath.endswith(".stf")):
					export_filepath += ".stf"

				# Create and write stf_file to disk
				stf_file = create_stf_binary_file(stf_context)
				files.append(open(export_filepath, "wb"))
				stf_file.serialize(files[len(files) - 1])

				if(self.debug):
					# Also write out the json itself for debugging purposes
					json_string = json.dumps(stf_file.definition.to_dict()).encode(encoding="utf-8")
					files.append(open(export_filepath + ".json", "wb"))
					files[len(files) - 1].write(json_string)

			elif(self.format == "json_contained"):
				export_filepath: str = self.filepath
				if(not export_filepath.endswith(".stf.json")):
					if(not export_filepath.endswith(".stf")):
						export_filepath += ".json"
					else:
						export_filepath += ".stf.json"

				stf_definition = create_stf_definition(stf_context, self.format)
				json_string = json.dumps(stf_definition.to_dict()).encode(encoding="utf-8")
				files.append(open(export_filepath, "wb"))
				files[len(files) - 1].write(json_string)

			elif(self.format == "json_seperate"):
				export_filepath: str = self.filepath
				if(not export_filepath.endswith(".stf.json")):
					if(not export_filepath.endswith(".stf")):
						export_filepath += ".json"
					else:
						export_filepath += ".stf.json"

				stf_definition = create_stf_definition(stf_context, self.format)
				# TODO generate all buffers as files as well
				json_string = json.dumps(stf_definition.to_dict()).encode(encoding="utf-8")
				files.append(open(export_filepath, "wb"))
				files[len(files) - 1].write(json_string)

			self.report({'INFO'}, "STF asset exported successfully!")
			return {"FINISHED"}
		except STFException as error:
			self.report({'ERROR'}, str(error))
			return {"CANCELLED"}
		finally:
			for file in files:
				if(file is not None and not file.closed): file.close()
			context.window.cursor_set('DEFAULT')

	def draw(self, context):
		self.layout.separator(factor=1, type="SPACE")
		self.layout.prop(self, property="format")
		if(self.format == "binary"):
			self.layout.prop(self, property="debug")

		self.layout.separator(factor=1, type="SPACE")
		self.layout.prop_search(bpy.context.scene, "stf_collection_selector", bpy.data, "collections", text="Root")
		self.layout.label(text="Remove Collection to export full scene")


def export_button(self, context):
	self.layout.operator(ExportSTF.bl_idname, text="STF (.stf/.stf.json)")


def register():
	bpy.types.TOPBAR_MT_file_export.append(export_button)

	bpy.types.Scene.stf_collection_selector = bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection", options={"SKIP_SAVE"}) # type: ignore

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(export_button)

	if hasattr(bpy.types.Scene, "stf_collection_selector"):
		del bpy.types.Scene.stf_collection_selector
