import json
import bpy

from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component


_stf_type = "com.vrchat.avatar_colliders"
_blender_property_name = "com_vrchat_avatar_colliders"


class VRC_AvatarColliders(STF_BlenderComponentBase):
	data: bpy.props.StringProperty(name="Data") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: VRC_AvatarColliders):
	layout.prop(component, "data")
	layout.label


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	component.data = str(json_resource)
	return component


def _stf_export(context: STF_ExportContext, application_object: VRC_AvatarColliders, parent_application_object: any) -> tuple[dict, str]:
	try:
		ret = json.loads(application_object.data)
		ret["type"] = _stf_type
		ret["name"] = application_object.stf_name
		return ret, application_object.stf_id
	except:
		return None


class STF_Module_VRC_AvatarColliders(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [VRC_AvatarColliders]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_VRC_AvatarColliders
]


def register():
	bpy.types.Collection.com_vrchat_avatar_colliders = bpy.props.CollectionProperty(type=VRC_AvatarColliders) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "com_vrchat_avatar_colliders"):
		del bpy.types.Collection.com_vrchat_avatar_colliders

