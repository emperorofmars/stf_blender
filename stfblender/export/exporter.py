import json
import bpy
from bpy_extras.io_utils import ExportHelper

from ...libstf.stf_registry import get_stf_processors
from ...libstf.stf_report import STFException
from ...libstf.stf_definition import STF_Meta_AssetInfo
from ...libstf.stf_export_context import STF_ExportContext, create_stf_binary_file, create_stf_definition

from .determine_export_root import determine_export_root_collection


class ExportSTF(bpy.types.Operator, ExportHelper):
	"""Export as STF file (.stf/.stf.json)"""
	bl_idname = "stf.export"
	bl_label = "Export STF"
	bl_options = {'PRESET'}
	bl_category = "STF"

	filename_ext = ".stf"
	filter_glob: bpy.props.StringProperty(default="*.stf;*.stf.json") # type: ignore

	format: bpy.props.EnumProperty(items=[("binary", "Binary", ""), ("json_contained", "Json (self contained)", ""), ("json_seperate", "Json (seperate buffers)", "")], default="binary", name="Format") # type: ignore

	root_collection: bpy.props.StringProperty(default="", name="Root Collection") # type: ignore

	debug: bpy.props.BoolProperty(name="Export Debug Json File", default=True) # type: ignore

	def invoke(self, context, event):
		if(context.scene.stf_root_collection):
			self.root_collection = context.scene.stf_root_collection.name
		return ExportHelper.invoke(self, context, event)

	def execute(self, context):
		context.window.cursor_set('WAIT')
		files = []
		try:
			# TODO: Save settings if wanted

			collection = determine_export_root_collection(self.root_collection)

			processors = get_stf_processors(bpy.context.preferences.addons.keys())

			# TODO: configure profiles, generate asset info
			stf_context = STF_ExportContext(profiles=[], asset_info=STF_Meta_AssetInfo(), processors=processors)

			# run modules to actually generate this definition
			stf_context.serialize_resource(collection)

			if(not stf_context.get_root_id()):
				raise Exception("Export Failed")

			if(self.format == "binary"):
				# Create and write stf_file to disk
				stf_file = create_stf_binary_file(stf_context)
				files.append(open(self.filepath, "wb"))
				stf_file.serialize(files[len(files) - 1])

				if(self.debug):
					# Also write out the json itself for debugging purposes
					json_string = json.dumps(stf_file.definition.to_dict()).encode(encoding="utf-8")
					files.append(open(self.filepath + ".json", "wb"))
					files[len(files) - 1].write(json_string)

			elif(self.format == "json_contained"):
				stf_definition = create_stf_definition(stf_context, self.format)
				json_string = json.dumps(stf_definition.to_dict()).encode(encoding="utf-8")
				files.append(open(self.filepath + ".stf.json", "wb"))
				files[len(files) - 1].write(json_string)

			elif(self.format == "json_seperate"):
				stf_definition = create_stf_definition(stf_context, self.format)
				# TODO generate all buffers as files as well
				json_string = json.dumps(stf_definition.to_dict()).encode(encoding="utf-8")
				files.append(open(self.filepath + ".stf.json", "wb"))
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
		self.layout.prop(self, property="format")
		if(self.format == "binary"):
			self.layout.prop(self, property="debug")
		self.layout.prop(self, property="root_collection")


def export_button(self, context):
	self.layout.operator(ExportSTF.bl_idname, text="STF (.stf/.stf.json)")

def register():
	bpy.types.TOPBAR_MT_file_export.append(export_button)

def unregister():
	bpy.types.TOPBAR_MT_file_export.remove(export_button)
