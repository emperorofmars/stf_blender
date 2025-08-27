import uuid
import bpy

from .....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_ExportComponentHook
from .....utils.component_utils import add_component, export_component_base, import_component_base
from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....utils.armature_bone import ArmatureBone


_stf_type = "org.blender.object.rotation_mode"
_blender_property_name = "org_blender_object_rotation_mode"


class Blender_Object_Rotation_Mode(STF_BlenderComponentBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Object) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)

	if("rotation_mode" in json_resource):
		def _callback():
			context_object.rotation_mode = json_resource["rotation_mode"]
		context.add_task(_callback)

	return component


def _stf_export(context: STF_ExportContext, component: Blender_Object_Rotation_Mode, context_object: bpy.types.Object) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["rotation_mode"] = context_object.rotation_mode
	return ret, component.stf_id


class STF_Module_Blender_Object_Rotation_Mode(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [Blender_Object_Rotation_Mode]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object]



def _hook_can_handle_func(application_object: bpy.types.Object) -> bool:
	if(hasattr(application_object, "org_blender_object_rotation_mode") and len(application_object.org_blender_object_rotation_mode) > 0): return False
	return True

def _hook_apply_func(context: STF_ExportContext, application_object: bpy.types.Object, context_object: any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_Blender_Object_Rotation_Mode(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Object]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func


register_stf_modules = [
	STF_Module_Blender_Object_Rotation_Mode,
	HOOK_Blender_Object_Rotation_Mode
]


def register():
	bpy.types.Object.org_blender_object_rotation_mode = bpy.props.CollectionProperty(type=Blender_Object_Rotation_Mode) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "org_blender_object_rotation_mode"):
		del bpy.types.Object.org_blender_object_rotation_mode
