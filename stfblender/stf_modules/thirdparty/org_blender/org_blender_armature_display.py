import uuid
import bpy

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_ExportComponentHook
from ....utils.component_utils import add_component, export_component_base, import_component_base
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext


_stf_type = "org.blender.armature.display"
_blender_property_name = "org_blender_armature_display"


class Blender_Armature_Display(STF_BlenderComponentBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Armature) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)

	if("bone_shape" in json_resource and str(json_resource["bone_shape"]).upper() in ['OCTAHEDRAL', 'STICK', 'BBONE', 'ENVELOPE', 'WIRE']):
		context_object.display_type = str(json_resource["bone_shape"]).upper()

	return component


def _stf_export(context: STF_ExportContext, component: Blender_Armature_Display, context_object: bpy.types.Armature) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["bone_shape"] = context_object.display_type.lower()
	return ret, component.stf_id


class STF_Module_Blender_Armature_Display(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [Blender_Armature_Display]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]



def _hook_can_handle_func(application_object: any) -> bool:
	armature: bpy.types.Armature = application_object
	if(armature.org_blender_armature_display and len(armature.org_blender_armature_display) > 0): return False
	return True

def _hook_apply_func(context: STF_ExportContext, application_object: bpy.types.Armature, context_object: any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_Blender_Armature_Display(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Armature]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func


register_stf_modules = [
	STF_Module_Blender_Armature_Display,
	HOOK_Blender_Armature_Display
]


def register():
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=Blender_Armature_Display))

def unregister():
	if hasattr(bpy.types.Armature, _blender_property_name):
		delattr(bpy.types.Armature, _blender_property_name)
