import bpy
import uuid
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_ExportComponentHook, STFReport, add_component, export_component_base, import_component_base


class Blender_Empty_Display(STF_ComponentResourceBase):
	pass


class Handler_Blender_Empty_Display(STF_Handler_Component):
	stf_type = "org.blender.empty.display"
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [Blender_Empty_Display]
	blender_property_name = "org_blender_empty_display"
	single = True
	filter = [bpy.types.Object]

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Object) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		if("empty_display_type" in json_resource):
			context_resource.empty_display_type = json_resource["empty_display_type"]
		if("empty_display_size" in json_resource):
			context_resource.empty_display_size = json_resource["empty_display_size"]
		# todo handle image display type

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Blender_Empty_Display, context_resource: bpy.types.Object) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, blender_resource, cls.blender_property_name, context_resource)
		ret["empty_display_type"] = context_resource.empty_display_type
		ret["empty_display_size"] = context_resource.empty_display_size
		# todo handle image display type
		return ret, blender_resource.stf_id


class Hook_Blender_Empty_Display(STF_ExportComponentHook):
	hook_understood_blender_types = [bpy.types.Object]

	@classmethod
	def hook_can_handle_blender_resource(cls, blender_resource: bpy.types.Object) -> bool:
		blender_object: bpy.types.Object = blender_resource
		if(blender_object.data is not None):
			return False
		if(hasattr(blender_object, Handler_Blender_Empty_Display.blender_property_name) and len(getattr(blender_object, Handler_Blender_Empty_Display.blender_property_name)) > 0):
			return False
		return True

	@classmethod
	def hook_export_resource(cls, context: STF_ExportContext, blender_resource: bpy.types.Object, context_resource: Any):
		add_component(blender_resource, Handler_Blender_Empty_Display.blender_property_name, str(uuid.uuid4()), Handler_Blender_Empty_Display.stf_type)


def register():
	setattr(bpy.types.Object, Handler_Blender_Empty_Display.blender_property_name, bpy.props.CollectionProperty(type=Blender_Empty_Display, options=set()))

def unregister():
	if hasattr(bpy.types.Object, Handler_Blender_Empty_Display.blender_property_name):
		delattr(bpy.types.Object, Handler_Blender_Empty_Display.blender_property_name)
