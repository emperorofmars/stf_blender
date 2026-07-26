import bpy
import uuid
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_ExportComponentHook, STFReport, add_component, export_component_base, import_component_base


class Blender_Armature_Display(STF_ComponentResourceBase):
	pass


class Handler_Blender_Armature_Display(STF_Handler_Component):
	stf_type = "org.blender.armature.display"
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [Blender_Armature_Display]
	blender_property_name = "org_blender_armature_display"
	single = True
	filter = [bpy.types.Armature]

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Armature) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		if("bone_shape" in json_resource and str(json_resource["bone_shape"]).upper() in ['OCTAHEDRAL', 'STICK', 'BBONE', 'ENVELOPE', 'WIRE']):
			context_resource.display_type = str(json_resource["bone_shape"]).upper()

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Blender_Armature_Display, context_resource: bpy.types.Armature) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, blender_resource, cls.blender_property_name, context_resource)
		ret["bone_shape"] = context_resource.display_type.lower()
		return ret, blender_resource.stf_id


class Hook_Blender_Armature_Display(STF_ExportComponentHook):
	hook_understood_blender_types = [bpy.types.Armature]

	@staticmethod
	def hook_can_handle_blender_resource(blender_resource: bpy.types.Armature) -> bool:
		if(hasattr(blender_resource, Handler_Blender_Armature_Display.blender_property_name) and len(getattr(blender_resource, Handler_Blender_Armature_Display.blender_property_name)) > 0): return False
		return True

	@staticmethod
	def hook_export_resource(context: STF_ExportContext, blender_resource: bpy.types.Armature, context_resource: Any):
		add_component(blender_resource, Handler_Blender_Armature_Display.blender_property_name, str(uuid.uuid4()), Handler_Blender_Armature_Display.stf_type)


def register():
	setattr(bpy.types.Armature, Handler_Blender_Armature_Display.blender_property_name, bpy.props.CollectionProperty(type=Blender_Armature_Display, options=set()))

def unregister():
	if hasattr(bpy.types.Armature, Handler_Blender_Armature_Display.blender_property_name):
		delattr(bpy.types.Armature, Handler_Blender_Armature_Display.blender_property_name)
