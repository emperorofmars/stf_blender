import bpy
import uuid
from typing import Any

from ....common import STF_ExportContext, STF_ImportContext, STF_Category
from ....common.resource.component import STF_ComponentResourceBase, STF_Handler_Component, STF_ExportComponentHook
from ....common.resource.component.component_utils import add_component, export_component_base, import_component_base


_stf_type = "org.blender.armature.display"
_blender_property_name = "org_blender_armature_display"


class Blender_Armature_Display(STF_ComponentResourceBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Armature) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	if("bone_shape" in json_resource and str(json_resource["bone_shape"]).upper() in ['OCTAHEDRAL', 'STICK', 'BBONE', 'ENVELOPE', 'WIRE']):
		context_object.display_type = str(json_resource["bone_shape"]).upper()

	return component


def _stf_export(context: STF_ExportContext, component: Blender_Armature_Display, context_object: bpy.types.Armature) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret["bone_shape"] = context_object.display_type.lower()
	return ret, component.stf_id


class STF_Module_Blender_Armature_Display(STF_Handler_Component):
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	understood_application_types = [Blender_Armature_Display]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]



def _hook_can_handle_func(application_object: Any) -> bool:
	armature: bpy.types.Armature = application_object
	if(armature.org_blender_armature_display and len(armature.org_blender_armature_display) > 0): return False
	return True

def _hook_apply_func(context: STF_ExportContext, application_object: bpy.types.Armature, context_object: Any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_Blender_Armature_Display(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Armature]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func


register_stf_handlers = [
	STF_Module_Blender_Armature_Display,
	HOOK_Blender_Armature_Display
]


def register():
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=Blender_Armature_Display, options=set()))

def unregister():
	if hasattr(bpy.types.Armature, _blender_property_name):
		delattr(bpy.types.Armature, _blender_property_name)
