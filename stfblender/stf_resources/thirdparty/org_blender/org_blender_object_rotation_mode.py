import bpy
import uuid
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_ExportComponentHook, add_component, export_component_base, import_component_base


class Blender_Object_Rotation_Mode(STF_ComponentResourceBase):
	pass


class Handler_Blender_Object_Rotation_Mode(STF_Handler_Component):
	stf_type = "org.blender.object.rotation_mode"
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [Blender_Object_Rotation_Mode]
	blender_property_name = "org_blender_object_rotation_mode"
	single = True
	filter = [bpy.types.Object]

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Object) -> Any:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		if("rotation_mode" in json_resource):
			def _callback():
				context_resource.rotation_mode = json_resource["rotation_mode"]
			context.add_task(STF_TaskSteps.DEFAULT, _callback)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Blender_Object_Rotation_Mode, context_resource: bpy.types.Object) -> tuple[dict, str]:
		ret = export_component_base(context, cls.stf_type, blender_resource, cls.blender_property_name, context_resource)
		ret["rotation_mode"] = context_resource.rotation_mode
		return ret, blender_resource.stf_id


class Hook_Blender_Object_Rotation_Mode(STF_ExportComponentHook):
	hook_understood_blender_types = [bpy.types.Object]

	@classmethod
	def hook_can_handle_blender_resource(cls, blender_resource: bpy.types.Object) -> bool:
		if(hasattr(blender_resource, Handler_Blender_Object_Rotation_Mode.blender_property_name) and len(getattr(blender_resource, Handler_Blender_Object_Rotation_Mode.blender_property_name)) > 0): return False
		return True

	@classmethod
	def hook_export_resource(cls, context: STF_ExportContext, blender_resource: bpy.types.Object, context_resource: Any):
		add_component(blender_resource, Handler_Blender_Object_Rotation_Mode.blender_property_name, str(uuid.uuid4()), Handler_Blender_Object_Rotation_Mode.stf_type)


def register():
	setattr(bpy.types.Object, Handler_Blender_Object_Rotation_Mode.blender_property_name, bpy.props.CollectionProperty(type=Blender_Object_Rotation_Mode, options=set()))

def unregister():
	if hasattr(bpy.types.Object, Handler_Blender_Object_Rotation_Mode.blender_property_name):
		delattr(bpy.types.Object, Handler_Blender_Object_Rotation_Mode.blender_property_name)
