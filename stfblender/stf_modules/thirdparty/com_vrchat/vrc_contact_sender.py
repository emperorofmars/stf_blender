import bpy

from .vrc_contact_utils import VRC_ContactBase, vrc_contact_draw_base, vrc_contact_export_base, vrc_contact_import_base
from ....base.stf_module_component import STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "com.vrchat.contact_sender"
_blender_property_name = "com_vrchat_contact_sender"


class VRC_ContactSender(VRC_ContactBase):
	pass


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_ContactSender):
	layout.use_property_split = True
	vrc_contact_draw_base(layout, context, component_ref, context_object, component, _blender_property_name)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	vrc_contact_import_base(context, component, json_resource)
	return component


def _stf_export(context: STF_ExportContext, component: VRC_ContactSender, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	vrc_contact_export_base(context, component, context_object, ret)
	return ret, component.stf_id


class STF_Module_VRC_ContactSender(STF_BlenderComponentModule):
	"""Represents a `VRCContactSender`.
	Serialize the component in Unity and paste the Json-definition into the `Set from JSON` operator"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [VRC_ContactSender]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	like_types = []

	pretty_name_template = "VRChat Contact Sender"


register_stf_modules = [
	STF_Module_VRC_ContactSender
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=VRC_ContactSender, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=VRC_ContactSender, options=set()))

def unregister():
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
