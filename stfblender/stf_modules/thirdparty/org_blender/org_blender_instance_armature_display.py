import uuid
import bpy

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_ExportComponentHook
from ....utils.component_utils import add_component, export_component_base, import_component_base
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext


_stf_type = "org.blender.instance.armature.display"
_blender_property_name = "org_blender_instance_armature_display"


class Blender_Instance_Armature_Display(STF_BlenderComponentBase):
	pass


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Object) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	if("display_in_front" in json_resource):
		context_object.show_in_front = json_resource["display_in_front"]

	return component


def _stf_export(context: STF_ExportContext, component: Blender_Instance_Armature_Display, context_object: bpy.types.Object) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret["display_in_front"] = context_object.show_in_front
	return ret, component.stf_id


class STF_Module_Blender_Armature_Display(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [Blender_Instance_Armature_Display]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object]



def _hook_can_handle_func(application_object: bpy.types.Object) -> bool:
	if(not type(application_object.data) is bpy.types.Armature): return False
	blender_object: bpy.types.Object = application_object
	if(blender_object.org_blender_instance_armature_display and len(blender_object.org_blender_instance_armature_display) > 0): return False
	return True

def _hook_apply_func(context: STF_ExportContext, application_object: bpy.types.Object, context_object: any):
	add_component(application_object, _blender_property_name, str(uuid.uuid4()), _stf_type)


class HOOK_Blender_Instance_Armature_Display(STF_ExportComponentHook):
	hook_target_application_types = [bpy.types.Object]
	hook_can_handle_application_object_func = _hook_can_handle_func
	hook_apply_func = _hook_apply_func


register_stf_modules = [
	STF_Module_Blender_Armature_Display,
	HOOK_Blender_Instance_Armature_Display
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=Blender_Instance_Armature_Display, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
