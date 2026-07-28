# pyright: reportAssignmentType=none

import bpy
import mathutils
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Handler_Animation, STF_Component_Ref, ComponentLoadJsonOperatorBase, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.utils.trs_utils import blender_translation_to_stf, stf_translation_to_blender
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection


_stf_type = "stfexp.collider.sphere"
_blender_property_name = "stfexp_collider_sphere"


class STFEXP_Collider_Sphere(STF_ComponentResourceBase):
	radius: bpy.props.FloatProperty(name="Radius", default=1, min=0, precision=3) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ", precision=3) # type: ignore


def _parse_json(component: STFEXP_Collider_Sphere, json_resource: dict):
	component.radius = json_resource.get("radius", 1)
	if("offset_position" in json_resource):
		offset_position = mathutils.Vector()
		for index in range(3):
			offset_position[index] = json_resource["offset_position"][index]
		component.offset_position = stf_translation_to_blender(offset_position) # pyright: ignore[reportArgumentType]

def _serialize_json(component: STFEXP_Collider_Sphere, json_resource: dict = {}) -> dict:
	json_resource["radius"] = component.radius
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	return json_resource


class STFEXP_Collider_Sphere_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.stfexp_collider_sphere_loadjson"
	blender_bone: bpy.props.BoolProperty() # type: ignore

	def get_property(self, context) -> Any:
		if(not self.blender_bone):
			return getattr(context.object, _blender_property_name)
		else:
			return getattr(context.bone, _blender_property_name)

	def parse_json(self, context, component: Any, json_resource: dict) -> set[str]: # pyright: ignore[reportIncompatibleMethodOverride]
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")
		_parse_json(component, json_resource)
		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Collider_Sphere):
	layout.use_property_split = True

	layout.prop(component, "radius")
	layout.prop(component, "offset_position")

	load_json_button = layout.operator(STFEXP_Collider_Sphere_LoadJsonOperator.bl_idname)
	load_json_button.blender_bone = type(component.id_data) is bpy.types.Armature
	load_json_button.component_id = component.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Collider_Sphere, component_instance: STFEXP_Collider_Sphere):
	component_instance.radius = component.radius
	component_instance.offset_position = component.offset_position


def _export_component_instance(context: STF_ExportContext, component_ref: STF_Component_Ref, component_instance: STFEXP_Collider_Sphere, context_resource: Any) -> dict:
	return _serialize_json(component_instance)

def _import_component_instance(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, component_instance: STFEXP_Collider_Sphere, context_resource: Any):
	_parse_json(component_instance, json_resource)


"""Import & export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
	component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_resource)
	_parse_json(component, json_resource) # pyright: ignore[reportArgumentType]
	return component

def _stf_export(context: STF_ExportContext, blender_resource: STFEXP_Collider_Sphere, context_resource: Any) -> tuple[dict, str] | STFReport:
	ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)
	ret = _serialize_json(blender_resource, ret)
	return ret, blender_resource.stf_id


"""Animation"""

def _export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None


def _import_stf_animation(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
	blender_resource = context.get_imported_resource(stf_property_path[0])
	component_index = get_component_index(blender_resource, _blender_property_name, blender_resource.stf_id)
	if(component_index is not None):
		match(stf_property_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
	return None


"""Handler definition"""

class Handler_STFEXP_Collider_Sphere(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""Sphere collider"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["collider.sphere", "collider"]
	understood_blender_types = [STFEXP_Collider_Sphere]
	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "Sphere Collider"

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
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Sphere))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Sphere))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
