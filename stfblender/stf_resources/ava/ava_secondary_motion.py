import bpy
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection


_stf_type = "ava.secondary_motion"
_blender_property_name = "ava_secondary_motion"


class AVA_SecondaryMotion(STF_ComponentResourceBase):
	intensity: bpy.props.FloatProperty(name="Intensity", default=0.3)


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: AVA_SecondaryMotion):
	layout.label(text="This component is mostly a stub for now.")
	layout.label(text="Use application specific bone-physics")
	layout.label(text="components if possible and override this one.")
	layout.prop(component, "intensity")


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: AVA_SecondaryMotion, component_instance: AVA_SecondaryMotion):
	component_instance.intensity = component.intensity


def _export_component_instance(context: STF_ExportContext, component_ref: STF_Component_Ref, component_instance: AVA_SecondaryMotion, context_resource: Any) -> dict:
	return {"intensity": component_instance.intensity}

def _import_component_instance(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, component_instance: AVA_SecondaryMotion, context_resource: Any):
	component_instance.intensity = json_resource.get("intensity", 0.3)


"""Import & export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
	component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_resource)
	component.intensity = json_resource.get("intensity")
	return component


def _stf_export(context: STF_ExportContext, blender_resource: AVA_SecondaryMotion, context_resource: Any) -> tuple[dict, str] | STFReport:
	ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)
	ret["intensity"] = blender_resource.intensity
	return ret, blender_resource.stf_id


"""Animation"""

def _export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None


def _import_stf_animation(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
	blender_object = context.get_imported_resource(stf_property_path[0])
	component_index = get_component_index(blender_resource, _blender_property_name, blender_object.stf_id)
	if(component_index is not None):
		match(stf_property_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
	return None


"""Module definition"""

class Handler_AVA_SecondaryMotion(STF_Handler_BoneComponent):
	"""Root of a physics chain"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["secondary_motion"]
	understood_blender_types = [AVA_SecondaryMotion]
	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "Secondary Motion"

	draw = _draw_component
	import_resource = _stf_import
	export_resource = _stf_export

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [_blender_property_name]
	export_blender_animation = _export_blender_animation
	import_stf_animation = _import_stf_animation

	draw_instance = _draw_component
	update_component_instance = _set_component_instance_standin

	export_component_instance = _export_component_instance
	import_component_instance = _import_component_instance


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=AVA_SecondaryMotion, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=AVA_SecondaryMotion, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
