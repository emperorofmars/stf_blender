import bpy
from typing import Any

from ...lib_stfblender import STF_ExportContext, STF_ImportContext, STF_TaskSteps
from ...lib_stfblender.module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...lib_stfblender.helpers import register_exported_resource, import_resource

from ...utils.component_utils import add_component, export_component_base, import_component_base
from ...utils.misc import SetActiveObjectOperator


_stf_type = "ava.voice_position"
_blender_property_name = "ava_voice_position"


class AVA_VoicePosition(STF_BlenderComponentBase):
	voice_position: bpy.props.PointerProperty(type=bpy.types.Object, name="Voice Position", description="This Object's location will be used to determine the voice position", options=set()) # type: ignore


class CreateVoicePositionObjectOperator(bpy.types.Operator):
	"""Create a voice-position object"""
	bl_idname = "ava.ava_voice_position_create_object"
	bl_label = "Create Position Object"
	bl_options = {"REGISTER", "UNDO"}

	blender_collection: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		target_object = bpy.data.collections[self.blender_collection]
		if("$VoicePosition" in bpy.data.objects):
			voice_object = bpy.data.objects["$VoicePosition"]
		else:
			voice_object = bpy.data.objects.new("$VoicePosition", None)
			voice_object.empty_display_size = 0.1
			voice_object.empty_display_type = "SINGLE_ARROW"
			target_object.objects.link(voice_object)
		for voice_component in getattr(target_object, _blender_property_name):
			if(voice_component.stf_id == self.component_id):
				voice_component.voice_position = voice_object
				break

		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: AVA_VoicePosition):
	layout.use_property_split = True
	if(component.voice_position):
		layout.prop(component, "voice_position")
		row = layout.row()
		row.alignment = "RIGHT"
		row.operator(SetActiveObjectOperator.bl_idname, text="Select Position Object", icon="EYEDROPPER").target_name = component.voice_position.name
	else:
		create_button = layout.operator(CreateVoicePositionObjectOperator.bl_idname, text="Create Position Object", icon="ADD")
		create_button.blender_collection = context_object.name
		create_button.component_id = component.stf_id


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	if("voice_position" in json_resource):
		def _handle():
			component.voice_position = import_resource(context, json_resource, json_resource["voice_position"], "node")
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, component: AVA_VoicePosition, context_object: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)

	if(component.voice_position):
		def _handle():
			ret["voice_position"] = register_exported_resource(ret, context.get_resource_id(component.voice_position))
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return ret, component.stf_id


class STF_Module_AVA_VoicePosition(STF_BlenderComponentModule):
	"""Specify the position from which a VR & V-Tubing avatars voice originates"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_VoicePosition]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = ["voice_position"]
	pretty_name_template = "Voice Position"


register_stf_modules = [
	STF_Module_AVA_VoicePosition
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=AVA_VoicePosition))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
