import json
import bpy

from .....exporter.stf_export_context import STF_ExportContext
from .....importer.stf_import_context import STF_ImportContext
from .....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base


_stf_type = "vrc.physbone"
_blender_property_name = "vrc_physbone"


class VRC_Physbone(STF_BlenderComponentBase):
	# todo ignores, colliders, etc..
	values: bpy.props.StringProperty(name="Json Values") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_Physbone):
	layout.prop(component, "values")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	component.values = json.dumps(json_resource["values"])
	# todo ignores, colliders, etc..
	return component


def _stf_export(context: STF_ExportContext, application_object: VRC_Physbone, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)
	ret["values"] = application_object.values
	# todo ignores, colliders, etc..
	return ret, application_object.stf_id


class STF_Module_VRC_Physbone(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["secondary_motion"]
	understood_application_types = [VRC_Physbone]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_VRC_Physbone
]


def register():
	bpy.types.Object.vrc_physbone = bpy.props.CollectionProperty(type=VRC_Physbone) # type: ignore
	bpy.types.Bone.vrc_physbone = bpy.props.CollectionProperty(type=VRC_Physbone) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "vrc_physbone"):
		del bpy.types.Object.vrc_physbone
	if hasattr(bpy.types.Bone, "vrc_physbone"):
		del bpy.types.Bone.vrc_physbone

