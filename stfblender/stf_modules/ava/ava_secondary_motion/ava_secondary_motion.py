import re
import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base


_stf_type = "ava.secondary_motion"
_blender_property_name = "ava_secondary_motion"


class AVA_SecondaryMotion(STF_BlenderComponentBase):
	intensity: bpy.props.FloatProperty(name="Intensity", default=0.3) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_SecondaryMotion):
	layout.label(text="This component is mostly a stub for now.")
	layout.label(text="Use application specific bone-physics")
	layout.label(text="components if possible and override this one.")
	layout.prop(component, "intensity")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	component.intensity = json_resource.get("intensity")
	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_SecondaryMotion, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)
	ret["intensity"] = application_object.intensity
	return ret, application_object.stf_id


class STF_Module_AVA_SecondaryMotion(STF_BlenderComponentModule):
	"""Root of a physics chain"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["secondary_motion"]
	understood_application_types = [AVA_SecondaryMotion]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_SecondaryMotion
]


def register():
	bpy.types.Object.ava_secondary_motion = bpy.props.CollectionProperty(type=AVA_SecondaryMotion) # type: ignore
	bpy.types.Bone.ava_secondary_motion = bpy.props.CollectionProperty(type=AVA_SecondaryMotion) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "ava_secondary_motion"):
		del bpy.types.Object.ava_secondary_motion
	if hasattr(bpy.types.Bone, "ava_secondary_motion"):
		del bpy.types.Bone.ava_secondary_motion

