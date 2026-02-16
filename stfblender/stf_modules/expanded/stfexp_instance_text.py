import bpy

from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...base.stf_module import STF_Module
from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui, ensure_stf_id
from ...base.stf_report import STFReportSeverity, STFReport
from ...utils.reference_helper import import_resource, register_exported_resource


_stf_type = "stfexp.instance.text"


class STFSetSTFEXPInstanceTextIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Text Instance"""
	bl_idname = "stf.set_stfexp_instance_text_stf_id"
	@classmethod
	def poll(cls, context): return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.TextCurve)
	def get_property(self, context): return context.object.stf_instance

class STFEXP_Instance_Text_Panel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stfexp_instance_text_editor"
	bl_label = "STF Editor: stfexp.instance.text"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "object"

	@classmethod
	def poll(cls, context):
		return context.object.stf_instance is not None and context.object.data and isinstance(context.object.data, bpy.types.TextCurve)

	def draw(self, context):
		# Set ID
		draw_stf_id_ui(self.layout, context, context.object.stf_instance, context.object.stf_instance, STFSetSTFEXPInstanceTextIDOperator.bl_idname, True)


"""
Import
"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_text = import_resource(context, json_resource, json_resource["text"], "data")

	blender_object = bpy.data.objects.new(json_resource.get("name", "STFEXP Instance Text"), blender_text)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_text))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import text", STFReportSeverity.Error, stf_id, _stf_type, context_object))

	# todo handle materials

	return blender_object


"""
Export
"""

def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and isinstance(application_object[1], bpy.types.TextCurve)):
		return 1000
	else:
		return -1


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_text: bpy.types.Text = application_object[1]
	ensure_stf_id(context, blender_object.stf_instance)

	ret = {
		"type": _stf_type,
		"name": blender_object.stf_instance.stf_name,
	}
	ret["text"] = register_exported_resource(ret, context.serialize_resource(blender_text, None, "data"))

	# todo handle materials

	return ret, blender_object.stf_instance.stf_id



"""
Definition
"""

class STF_Module_STFEXP_Instance_Text(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["instance.text"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func


register_stf_modules = [
	STF_Module_STFEXP_Instance_Text
]

def register():
	pass

def unregister():
	pass
