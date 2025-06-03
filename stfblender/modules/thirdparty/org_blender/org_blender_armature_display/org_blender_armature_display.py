import uuid
import bpy

from .....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, add_component
from .....core.stf_module import STF_ExportComponentHook
from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....core.buffer_utils import parse_uint, serialize_uint


_stf_type = "org.blender.armature.display"
_blender_property_name = "org_blender_armature_display"


class Blender_Armature_Display(STF_BlenderComponentBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Armature) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)

	if("bone_shape" in json_resource and str(json_resource["bone_shape"]).upper() in ['OCTAHEDRAL', 'STICK', 'BBONE', 'ENVELOPE', 'WIRE']):
		context_object.display_type = str(json_resource["bone_shape"]).upper()

	return component


def _stf_export(context: STF_ExportContext, application_object: Blender_Armature_Display, context_object: bpy.types.Armature) -> tuple[dict, str]:
	ret = {
		"type": _stf_type,
		"bone_shape": context_object.display_type.lower(),
	}
	return ret, application_object.stf_id


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
	bpy.types.Armature.org_blender_armature_display = bpy.props.CollectionProperty(type=Blender_Armature_Display) # type: ignore

def unregister():
	if hasattr(bpy.types.Armature, "org_blender_armature_display"):
		del bpy.types.Armature.org_blender_armature_display
