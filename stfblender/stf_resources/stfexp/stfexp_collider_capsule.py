import bpy
import mathutils
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Handler_Animation, STF_Component_Ref, ComponentLoadJsonOperatorBase, STFReport, add_component, export_component_base, import_component_base
from ....stfblender_common.utils.trs_utils import blender_rotation_to_stf, blender_translation_to_stf, stf_rotation_to_blender, stf_translation_to_blender
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection


class STFEXP_Collider_Capsule(STF_ComponentResourceBase):
	radius: bpy.props.FloatProperty(name="Radius", default=1, min=0, precision=3)
	height: bpy.props.FloatProperty(name="Height", default=1, min=0, precision=3)
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ")
	offset_rotation: bpy.props.FloatVectorProperty(name="Rotation Offset", size=3, default=(0, 0, 0), subtype="EULER")


def _parse_json(component: STFEXP_Collider_Capsule, json_resource: dict):
	component.radius = json_resource.get("radius", 1)
	component.height = json_resource.get("height", 1)
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

def _serialize_json(component: STFEXP_Collider_Capsule, json_resource: dict = {}) -> dict:
	json_resource["radius"] = component.radius
	json_resource["height"] = component.height
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	offset_rotation = mathutils.Euler(component.offset_rotation)
	json_resource["offset_rotation"] = blender_rotation_to_stf(offset_rotation.to_quaternion())
	return json_resource


class STFEXP_Collider_Capsule_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.stfexp_collider_capsule_loadjson"
	blender_bone: bpy.props.BoolProperty()

	def get_property(self, context) -> Any:
		if(not self.blender_bone):
			return getattr(context.object, Handler_STFEXP_Collider_Capsule.blender_property_name)
		else:
			return getattr(context.bone, Handler_STFEXP_Collider_Capsule.blender_property_name)

	def parse_json(self, context, component: Any, json_resource: dict) -> set[str]:  # pyright: ignore[reportIncompatibleMethodOverride]
		if(json_resource.get("type") != Handler_STFEXP_Collider_Capsule.stf_type): raise Exception("Invalid Type")
		_parse_json(component, json_resource)
		return {"FINISHED"}


class Handler_STFEXP_Collider_Capsule(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""Capsule collider"""
	stf_type = "stfexp.collider.capsule"
	stf_category = STF_Category.COMPONENT
	like_types = ["collider.capsule", "collider"]
	understood_blender_types = [STFEXP_Collider_Capsule]
	blender_property_name = "stfexp_collider_capsule"
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "Capsule Collider"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: Any) -> None:
		layout.use_property_split = True

		layout.prop(component, "radius")
		layout.prop(component, "height")
		layout.prop(component, "offset_position")
		layout.prop(component, "offset_rotation")

		load_json_button = layout.operator(STFEXP_Collider_Capsule_LoadJsonOperator.bl_idname)
		load_json_button.blender_bone = type(component.id_data) is bpy.types.Armature
		load_json_button.component_id = component.stf_id

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		_parse_json(component, json_resource)  # pyright: ignore[reportArgumentType]
		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, blender_resource, cls.blender_property_name, context_resource)
		ret = _serialize_json(blender_resource, ret)
		return ret, blender_resource.stf_id

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [blender_property_name]

	@classmethod
	def export_blender_animation(cls, context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
		if(match := re.search(r"^" + cls.blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
			if(component_path := get_component_stf_path_from_collection(blender_resource, cls.blender_property_name, int(match.groupdict()["component_index"]))):
				return STFPropertyPathPart(component_path + ["enabled"])
		return None

	@classmethod
	def import_stf_animation(cls, context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
		blender_resource = context.get_imported_resource(stf_property_path[0])
		component_index = get_component_index(blender_resource, cls.blender_property_name, blender_resource.stf_id)
		if(component_index is not None):
			match(stf_property_path[1]):
				case "enabled":
					return BlenderPropertyPathPart("OBJECT", cls.blender_property_name + "[" + str(component_index) + "].enabled")
		return None

	@classmethod
	def update_component_instance(cls, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Collider_Capsule, component_instance: STFEXP_Collider_Capsule) -> None:
		component_instance.radius = component.radius
		component_instance.height = component.height
		component_instance.offset_position = component.offset_position
		component_instance.offset_rotation = component.offset_rotation

	@classmethod
	def export_component_instance(cls, context: STF_ExportContext, component_ref: STF_Component_Ref, component_instance: Any, context_resource: Any) -> dict:
		return _serialize_json(component_instance)

	@classmethod
	def import_component_instance(cls, context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, component_instance: STFEXP_Collider_Capsule, context_resource: Any) -> None:
		_parse_json(component_instance, json_resource)


def register():
	setattr(bpy.types.Object, Handler_STFEXP_Collider_Capsule.blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Capsule))
	setattr(bpy.types.Bone, Handler_STFEXP_Collider_Capsule.blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Collider_Capsule))

def unregister():
	if hasattr(bpy.types.Object, Handler_STFEXP_Collider_Capsule.blender_property_name):
		delattr(bpy.types.Object, Handler_STFEXP_Collider_Capsule.blender_property_name)
	if hasattr(bpy.types.Bone, Handler_STFEXP_Collider_Capsule.blender_property_name):
		delattr(bpy.types.Bone, Handler_STFEXP_Collider_Capsule.blender_property_name)
