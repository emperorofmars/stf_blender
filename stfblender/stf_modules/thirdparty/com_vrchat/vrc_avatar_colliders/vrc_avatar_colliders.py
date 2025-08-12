import json
import bpy

from .....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....utils.component_utils import add_component, import_component_base
from .....utils.id_utils import ensure_stf_id


_stf_type = "com.vrchat.avatar_colliders"
_blender_property_name = "com_vrchat_avatar_colliders"


class VRC_AvatarColliders(STF_BlenderComponentBase):
	data: bpy.props.StringProperty(name="Data") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_AvatarColliders):
	layout.prop(component, "data")
	layout.label


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	component.data = json.dumps(json_resource)
	import_component_base(component, json_resource)
	return component


def _stf_export(context: STF_ExportContext, component: VRC_AvatarColliders, context_object: any) -> tuple[dict, str]:
	try:
		ensure_stf_id(context, component, component)
		ret = json.loads(component.data)
		ret["type"] = _stf_type
		ret["name"] = component.stf_name
		ret["overrides"] = [override.target_id for override in component.overrides]
		return ret, component.stf_id
	except:
		return None


class STF_Module_VRC_AvatarColliders(STF_BlenderComponentModule):
	"""Represents the `Colliders` of an `VRCAvatarDescriptor`.
	Serialize the component in Unity and paste the Json-definition into the `Data` field"""
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

