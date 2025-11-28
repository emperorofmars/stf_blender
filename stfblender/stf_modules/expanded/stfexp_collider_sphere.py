import re
from typing import Callable
import bpy
import mathutils

from ...base.property_path_part import STFPropertyPathPart
from ...base.stf_module_component import STF_BlenderBoneComponentModule, STF_BlenderComponentBase, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import ComponentLoadJsonOperatorBase, add_component, export_component_base, import_component_base
from ...utils.trs_utils import blender_translation_to_stf, stf_translation_to_blender
from ...utils.animation_conversion_utils import get_component_index, get_component_stf_path, get_component_stf_path_from_collection


_stf_type = "stfexp.collider.sphere"
_blender_property_name = "stfexp_collider_sphere"


class STFEXP_Collider_Sphere(STF_BlenderComponentBase):
	radius: bpy.props.FloatProperty(name="Radius", default=1) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ") # type: ignore


def _parse_json(component: STFEXP_Collider_Sphere, json_resource: dict):
	component.radius = json_resource.get("radius", 1)
	if("offset_position" in json_resource):
		offset_position = mathutils.Vector()
		for index in range(3):
			offset_position[index] = json_resource["offset_position"][index]
		component.offset_position = stf_translation_to_blender(offset_position)

def _serialize_json(component: STFEXP_Collider_Sphere, json_resource: dict = {}) -> dict:
	json_resource["radius"] = component.radius
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	return json_resource


class STFEXP_Collider_Sphere_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.stfexp_collider_sphere_loadjson"
	blender_bone: bpy.props.BoolProperty() # type: ignore

	def get_property(self, context) -> any:
		if(not self.blender_bone):
			return context.object.stfexp_collider_sphere
		else:
			return context.bone.stfexp_collider_sphere

	def parse_json(self, context, component: any, json_resource: dict):
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")
		_parse_json(component, json_resource)
		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Collider_Sphere):
	layout.use_property_split = True
	layout.prop(component, "radius")
	layout.prop(component, "offset_position")
	
	load_json_button = layout.operator(STFEXP_Collider_Sphere_LoadJsonOperator.bl_idname)
	load_json_button.blender_bone = type(component.id_data) == bpy.types.Armature
	load_json_button.component_id = component.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Collider_Sphere, standin_component: STFEXP_Collider_Sphere):
	standin_component.radius = component.radius
	standin_component.offset_position = component.offset_position


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Collider_Sphere, context_object: any) -> dict:
	return _serialize_json(standin_component)

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Collider_Sphere, context_object: any):
	_parse_json(standin_component, json_resource)


"""Import & export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, context_object)
	_parse_json(component, json_resource)
	return component

def _stf_export(context: STF_ExportContext, component: STFEXP_Collider_Sphere, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret = _serialize_json(component, ret)
	return ret, component.stf_id


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	if(component_index := get_component_index(application_object, _blender_property_name, blender_object.stf_id)):
		match(stf_path[1]):
			case "enabled":
				return None, 0, "OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled", None, None
	return None


"""Module definition"""

class STF_Module_STFEXP_Collider_Sphere(STF_BlenderBoneComponentModule):
	"""Sphere collider"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["collider.sphere", "collider"]
	understood_application_types = [STFEXP_Collider_Sphere]
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

	serialize_component_instance_standin_func = _serialize_component_instance_standin_func
	parse_component_instance_standin_func = _parse_component_instance_standin_func


register_stf_modules = [
	STF_Module_STFEXP_Collider_Sphere
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Sphere))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Sphere))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
