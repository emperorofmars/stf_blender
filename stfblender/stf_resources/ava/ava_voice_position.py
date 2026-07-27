import bpy
import uuid
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.helpers import register_exported_resource, OP_SetActiveObjectOperator
from ..stfexp import stfexp_node_ethereal


_stf_type = "ava.voice_position"
_blender_property_name = "ava_voice_position"


class AVA_VoicePosition(STF_ComponentResourceBase):
	voice_position: bpy.props.PointerProperty(type=bpy.types.Object, name="Voice Position", description="This Object's location will be used to determine the voice position", options=set()) # type: ignore


class CreateVoicePositionObjectOperator(bpy.types.Operator):
	"""Create a voice-position object"""
	bl_idname = "ava.ava_voice_position_create_object"
	bl_label = "Create Position Object"
	bl_options = {"REGISTER", "UNDO"}

	blender_collection: bpy.props.StringProperty() # type: ignore
	component_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context) -> set:
		target_object = bpy.data.collections[self.blender_collection]
		if("$VoicePosition" in bpy.data.objects):
			voice_object = bpy.data.objects["$VoicePosition"]
		else:
			voice_object = bpy.data.objects.new("$VoicePosition", None)
			voice_object.rotation_mode = "QUATERNION"
			voice_object.empty_display_size = 0.1
			voice_object.empty_display_type = "SINGLE_ARROW"
			add_component(voice_object, stfexp_node_ethereal._blender_property_name, str(uuid.uuid4()), stfexp_node_ethereal._stf_type)
			target_object.objects.link(voice_object)
		for voice_component in getattr(target_object, _blender_property_name):
			if(voice_component.stf_id == self.component_id):
				voice_component.voice_position = voice_object
				break

		return {"FINISHED"}


class Handler_AVA_VoicePosition(STF_Handler_Component):
	"""Specify the position from which a VR & V-Tubing avatars voice originates"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["voice_position"]
	understood_blender_types = [AVA_VoicePosition]
	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	pretty_name_template = "Voice Position"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: AVA_VoicePosition):
		layout.use_property_split = True
		if(component.voice_position):
			layout.prop(component, "voice_position")
			row = layout.row()
			row.alignment = "RIGHT"
			row.operator(OP_SetActiveObjectOperator, text="Select Position Object", icon="EYEDROPPER").target_name = component.voice_position.name
		else:
			create_button = layout.operator(CreateVoicePositionObjectOperator.bl_idname, text="Create Position Object", icon="ADD")
			create_button.blender_collection = context_resource.name
			create_button.component_id = component.stf_id

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		if("voice_position" in json_resource):
			def _handle():
				component.voice_position = context.import_resource(json_resource, json_resource["voice_position"], STF_Category.NODE)
			context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: AVA_VoicePosition, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)

		if(component.voice_position):
			def _handle():
				ret["voice_position"] = register_exported_resource(ret, context.get_resource_id(component.voice_position)) # pyright: ignore[reportArgumentType]
			context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return ret, component.stf_id


def register():
	setattr(bpy.types.Collection, Handler_AVA_VoicePosition.blender_property_name, bpy.props.CollectionProperty(type=AVA_VoicePosition))

def unregister():
	if hasattr(bpy.types.Collection, Handler_AVA_VoicePosition.blender_property_name):
		delattr(bpy.types.Collection, Handler_AVA_VoicePosition.blender_property_name)
