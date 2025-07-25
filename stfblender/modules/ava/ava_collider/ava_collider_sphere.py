import re
from typing import Callable
import bpy
import mathutils

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import ComponentLoadJsonOperatorBase, STF_BlenderBoneComponentModule, STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....utils.trs_utils import blender_translation_to_stf, stf_translation_to_blender
from ....utils.animation_conversion_utils import get_component_stf_path


_stf_type = "ava.collider.sphere"
_blender_property_name = "ava_collider_sphere"


class AVA_Collider_Sphere(STF_BlenderComponentBase):
	radius: bpy.props.FloatProperty(name="Radius", default=1) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ") # type: ignore


def _parse_json(component: AVA_Collider_Sphere, json_resource: dict):
	component.radius = json_resource.get("radius", 1)
	if("offset_position" in json_resource):
		offset_position = mathutils.Vector()
		for index in range(3):
			offset_position[index] = json_resource["offset_position"][index]
		component.offset_position = stf_translation_to_blender(offset_position)


def _serialize_json(component: AVA_Collider_Sphere, json_resource: dict = {}) -> dict:
	json_resource["radius"] = component.radius
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	return json_resource


class AVA_Collider_Sphere_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.ava_collider_sphere_loadjson"
	blender_bone: bpy.props.BoolProperty() # type: ignore

	def get_property(self, context) -> any:
		if(not self.blender_bone):
			return context.object.ava_collider_sphere
		else:
			return context.bone.ava_collider_sphere

	def parse_json(self, context, component: any, json_resource: dict):
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")
		_parse_json(component, json_resource)
		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Collider_Sphere):
	layout.prop(component, "radius")
	layout.prop(component, "offset_position")
	
	load_json_button = layout.operator(AVA_Collider_Sphere_LoadJsonOperator.bl_idname)
	load_json_button.blender_bone = type(component.id_data) == bpy.types.Armature
	load_json_button.component_id = component.stf_id


def _draw_component_instance(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Collider_Sphere):
	layout.prop(component, "radius")
	layout.prop(component, "offset_position")
	
	load_json_button = layout.operator(AVA_Collider_Sphere_LoadJsonOperator.bl_idname)
	load_json_button.blender_bone = type(component.id_data) == bpy.types.Armature
	load_json_button.component_id = component.stf_id


def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Collider_Sphere, standin_component: AVA_Collider_Sphere):
	standin_component.radius = component.radius
	standin_component.offset_position = component.offset_position


def _serialize_component_instance_standin_func(context: bpy.types.Context, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentModule, context_object: any) -> dict:
	return _serialize_json(standin_component)

def _parse_component_instance_standin_func(context: bpy.types.Context, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentModule, context_object: any):
	_parse_json(standin_component, json_resource)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	_parse_json(component, json_resource)
	return component


def _stf_export(context: STF_ExportContext, component: AVA_Collider_Sphere, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, component)
	ret["radius"] = component.radius

	offset_position = mathutils.Vector(component.offset_position)
	ret["offset_position"] = blender_translation_to_stf(offset_position)
	return ret, component.stf_id


def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^ava_collider_sphere\[(?P<component_index>[\d]+)\].enabled", data_path)):
		component = application_object.ava_collider_sphere[int(match.groupdict()["component_index"])]
		component_path = get_component_stf_path(application_object, component)
		if(component_path):
			return component_path + ["enabled"], None, None
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[int, any], any]]:
	blender_object = context.get_imported_resource(stf_path[0])
	# let component_index
	for component_index, component in enumerate(application_object.ava_collider_sphere):
		if(component.stf_id == blender_object.stf_id):
			break
	match(stf_path[1]):
		case "enabled":
			return None, 0, "OBJECT", "ava_collider_sphere[" + str(component_index) + "].enabled", 0, None
	return None


class STF_Module_AVA_Collider_Sphere(STF_BlenderBoneComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["collider.sphere", "collider"]
	understood_application_types = [AVA_Collider_Sphere]
	import_func = _stf_import
	export_func = _stf_export

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = [_blender_property_name]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	draw_component_instance_func = _draw_component_instance
	set_component_instance_standin_func = _set_component_instance_standin

	serialize_component_instance_standin_func = _serialize_component_instance_standin_func
	parse_component_instance_standin_func = _parse_component_instance_standin_func


register_stf_modules = [
	STF_Module_AVA_Collider_Sphere
]


def register():
	bpy.types.Object.ava_collider_sphere = bpy.props.CollectionProperty(type=AVA_Collider_Sphere) # type: ignore
	bpy.types.Bone.ava_collider_sphere = bpy.props.CollectionProperty(type=AVA_Collider_Sphere) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "ava_collider_sphere"):
		del bpy.types.Object.ava_collider_sphere
	if hasattr(bpy.types.Bone, "ava_collider_sphere"):
		del bpy.types.Bone.ava_collider_sphere

