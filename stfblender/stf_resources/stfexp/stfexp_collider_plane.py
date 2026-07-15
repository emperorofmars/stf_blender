import bpy
import mathutils
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STFReport, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Handler_Animation, STF_Component_Ref, ComponentLoadJsonOperatorBase, add_component, export_component_base, import_component_base
from ....stfblender_common.utils.trs_utils import blender_rotation_to_stf, blender_translation_to_stf, stf_rotation_to_blender, stf_translation_to_blender
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection

_stf_type = "stfexp.collider.plane"
_blender_property_name = "stfexp_collider_plane"


class STFEXP_Collider_Plane(STF_ComponentResourceBase):
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ", precision=3) # type: ignore
	offset_rotation: bpy.props.FloatVectorProperty(name="Rotation Offset", size=3, default=(0, 0, 0), subtype="EULER", precision=3) # type: ignore


def _parse_json(component: STFEXP_Collider_Plane, json_resource: dict):
	if("offset_position" in json_resource):
		offset_position = mathutils.Vector()
		for index in range(3):
			offset_position[index] = json_resource["offset_position"][index]
		component.offset_position = stf_translation_to_blender(offset_position)  # pyright: ignore[reportArgumentType]

	if("offset_rotation" in json_resource):
		offset_rotation = mathutils.Vector((0, 0, 0, 0))
		for index in range(4):
			offset_rotation[index] = json_resource["offset_rotation"][index]
		component.offset_rotation = stf_rotation_to_blender(offset_rotation).to_euler("XYZ")  # pyright: ignore[reportArgumentType]

def _serialize_json(component: STFEXP_Collider_Plane, json_resource: dict = {}) -> dict:
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	offset_rotation = mathutils.Euler(component.offset_rotation)
	json_resource["offset_rotation"] = blender_rotation_to_stf(offset_rotation.to_quaternion())
	return json_resource


class STFEXP_Collider_Plane_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.stfexp_collider_plane_loadjson"
	blender_bone: bpy.props.BoolProperty() # type: ignore

	def get_property(self, context) -> Any:
		if(not self.blender_bone):
			return getattr(context.object, _blender_property_name)
		else:
			return getattr(context.bone, _blender_property_name)

	def parse_json(self, context, component: Any, json_resource: dict) -> set[str]:  # pyright: ignore[reportIncompatibleMethodOverride]
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")
		_parse_json(component, json_resource)
		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_ComponentResourceBase): # pyright: ignore[reportRedeclaration]
	component: STFEXP_Collider_Plane = component # pyright: ignore[reportAssignmentType]
	layout.use_property_split = True
	layout.prop(component, "offset_position")
	layout.prop(component, "offset_rotation")

	load_json_button = layout.operator(STFEXP_Collider_Plane_LoadJsonOperator.bl_idname)
	load_json_button.blender_bone = type(component.id_data) is bpy.types.Armature
	load_json_button.component_id = component.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STFEXP_Collider_Plane, standin_component: STFEXP_Collider_Plane):
	standin_component.offset_position = component.offset_position
	standin_component.offset_rotation = component.offset_rotation


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Collider_Plane, context_object: Any) -> dict:
	return _serialize_json(standin_component)

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Collider_Plane, context_object: Any):
	_parse_json(standin_component, json_resource)


"""Import & export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	_parse_json(component, json_resource)  # pyright: ignore[reportArgumentType]
	return component

def _stf_export(context: STF_ExportContext, blender_object: STFEXP_Collider_Plane, context_object: Any) -> tuple[dict, str] | STFReport:
	component = blender_object
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret = _serialize_json(component, ret)
	return ret, component.stf_id


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, blender_object: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_property_path: list[str], blender_object: Any) -> BlenderPropertyPathPart | None:
	blender_object = context.get_imported_resource(stf_property_path[0])
	component_index = get_component_index(blender_object, _blender_property_name, blender_object.stf_id)
	if(component_index is not None):
		match(stf_property_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
	return None


"""Handler definition"""

class Handler_STFEXP_Collider_Plane(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""Infinitely big plane collider"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["collider.plane", "collider"]
	understood_application_types = [STFEXP_Collider_Plane]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = [_blender_property_name]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

	draw_component_instance_func = _draw_component
	set_component_instance_standin_func = _set_component_instance_standin

	serialize_component_instance_standin_func = _serialize_component_instance_standin_func  # pyright: ignore[reportAssignmentType]
	parse_component_instance_standin_func = _parse_component_instance_standin_func  # pyright: ignore[reportAssignmentType]

	pretty_name_template = "Plane Collider"


register_stf_handlers = [
	Handler_STFEXP_Collider_Plane
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Plane))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Plane))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
