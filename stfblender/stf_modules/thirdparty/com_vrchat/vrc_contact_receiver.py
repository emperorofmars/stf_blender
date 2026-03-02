import json
import bpy

from .vrc_contact_utils import VRC_ContactBase, vrc_contact_draw_base, vrc_contact_export_base, vrc_contact_import_base
from ....base.stf_module_component import STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "com.vrchat.contact_receiver"
_blender_property_name = "com_vrchat_contact_receiver"


class VRC_ContactReceiver(VRC_ContactBase):
	receiver_type: bpy.props.EnumProperty(name="Receiver Type", items=(("constant", "Constant", ""), ("on_enter", "On Enter", ""), ("proximity", "Proximity", "")), default="constant", options=set()) # type: ignore
	parameter: bpy.props.StringProperty(name="Parameter", options=set()) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_ContactReceiver):
	layout.use_property_split = True
	vrc_contact_draw_base(layout, context, component_ref, context_object, component, _blender_property_name)

	col = layout.column(align=True)
	col.prop(component, "receiver_type")
	col.prop(component, "parameter")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	vrc_contact_import_base(context, component, json_resource)
	component.receiver_type = json_resource.get("receiver_type", "constant")
	component.parameter = json_resource.get("parameter", "")
	return component


def _stf_export(context: STF_ExportContext, component: VRC_ContactReceiver, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	vrc_contact_export_base(context, component, context_object, ret)
	ret["receiver_type"] = component.receiver_type
	ret["parameter"] = component.parameter
	return ret, component.stf_id


class STF_Module_VRC_ContactReceiver(STF_BlenderComponentModule):
	"""Represents a `VRCContactSender`.
	Serialize the component in Unity and paste the Json-definition into the `Set from JSON` operator"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [VRC_ContactReceiver]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	like_types = []

	pretty_name_template = "VRChat Contact Receiver"


register_stf_modules = [
	STF_Module_VRC_ContactReceiver
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=VRC_ContactReceiver, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=VRC_ContactReceiver, options=set()))

def unregister():
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
