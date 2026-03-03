import bpy
import mathutils
import re
from typing import Any, Callable

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.helpers import create_add_button, create_remove_button
from ....base.stf_module_component import STF_BlenderComponentBase, STF_Component_Ref
from ....utils.trs_utils import blender_rotation_to_stf, blender_translation_to_stf, stf_rotation_to_blender, stf_translation_to_blender
from ....utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from ....base.property_path_part import BlenderPropertyPathPart, STFPropertyPathPart


def search_collision_tags(self, context: bpy.types.Context, edit_text: str):
	return [
		"Head",
		"Torso",
		"Hand",
		"HandL",
		"HandR",
		"Foot",
		"FootL",
		"FootR",
		"Finger",
		"FingerL",
		"FingerR",
		"FingerIndex",
		"FingerMiddle",
		"FingerRing",
		"FingerLittle",
		"FingerIndexL",
		"FingerMiddleL",
		"FingerRingL",
		"FingerLittleL",
		"FingerIndexR",
		"FingerMiddleR",
		"FingerRingR",
		"FingerLittleR",
		"Hot",
		"Cold",
		"Fire",
		"Freezer",
		"Wet",
		"Water",
		"Wind",
		"Combat",
		"Weapon",
		"Shield",
		"Damage",
		"DamageBlunt",
		"DamageSharp",
		"Ammunition",
		"Projectile",
		"Interaction",
		"Consumable",
		"ConsumableFood",
		"ConsumableDrink",
		"Brush",
		"Dye",
	]


class CollisionTag(bpy.types.PropertyGroup):
	tag_name: bpy.props.StringProperty(name="Tag", options=set(), search=search_collision_tags) # type: ignore


class VRC_ContactBase(STF_BlenderComponentBase):
	shape: bpy.props.EnumProperty(name="Shape", items=(("sphere", "Sphere", ""), ("capsule", "Capsule", "")), default="sphere", options=set()) # type: ignore
	radius: bpy.props.FloatProperty(name="Radius", default=1, min=0, precision=3) # type: ignore
	height: bpy.props.FloatProperty(name="Height", default=1, min=0, precision=3) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ", precision=3) # type: ignore
	offset_rotation: bpy.props.FloatVectorProperty(name="Rotation Offset", size=3, default=(0, 0, 0), subtype="EULER", precision=3) # type: ignore
	filter_avatar: bpy.props.BoolProperty(name="Avatar", default=False, options=set()) # type: ignore
	filter_world: bpy.props.BoolProperty(name="World", default=False, options=set()) # type: ignore
	local_only: bpy.props.BoolProperty(name="Local Only", default=False, options=set()) # type: ignore
	collision_tags: bpy.props.CollectionProperty(name="Collision Tags", type=CollisionTag, options=set()) # type: ignore


def vrc_contact_draw_base(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: VRC_ContactBase, blender_property_name: str):
	col = layout.column(align=True)
	col.prop(component, "shape")
	col.prop(component, "radius")
	if(component.shape == "capsule"):
		col.prop(component, "height")

	layout.prop(component, "offset_position")
	if(component.shape == "capsule"):
		layout.prop(component, "offset_rotation")

	row = layout.row(align=True, heading="Filter")
	row.prop(component, "filter_avatar", toggle=True)
	row.prop(component, "filter_world", toggle=True)
	row.prop(component, "local_only", toggle=True)

	box = layout.box()
	box.label(text="Collision Tags")
	col = box.column(align=True)
	for index_coltag, coltag in enumerate(component.collision_tags):
		row = col.row(align=True)
		row.prop(coltag, "tag_name")
		create_remove_button(row, "object" if type(component.id_data) == bpy.types.Object else "bone", blender_property_name, component.stf_id, "collision_tags", index_coltag)
	create_add_button(box, "object" if type(component.id_data) == bpy.types.Object else "bone", blender_property_name, component.stf_id, "collision_tags")


def vrc_contact_import_base(component: VRC_ContactBase, json_resource: dict):
	component.shape = json_resource.get("shape", "sphere")
	component.radius = json_resource.get("radius", 1)
	component.height = json_resource.get("height", 1)
	if("offset_position" in json_resource):
		offset_position = mathutils.Vector()
		for index in range(3):
			offset_position[index] = json_resource["offset_position"][index]
		component.offset_position = stf_translation_to_blender(offset_position)
	if("offset_rotation" in json_resource):
		offset_rotation = mathutils.Vector((0, 0, 0, 0))
		for index in range(4):
			offset_rotation[index] = json_resource["offset_rotation"][index]
		component.offset_rotation = stf_rotation_to_blender(offset_rotation).to_euler("XYZ")

	component.filter_avatar = json_resource.get("filter_avatar", False)
	component.filter_world = json_resource.get("filter_world", False)
	component.local_only = json_resource.get("local_only", False)

	component.collision_tags.clear()
	for coltag in json_resource.get("collision_tags", []):
		new_tag = component.collision_tags.add()
		new_tag.name = coltag
		new_tag.tag_name = coltag


def vrc_contact_export_base(component: VRC_ContactBase, context_object: Any, json_resource: dict):
	json_resource["shape"] = component.shape
	json_resource["radius"] = component.radius
	if(component.shape == "capsule"):
		json_resource["height"] = component.height
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	if(component.shape == "capsule"):
		offset_rotation = mathutils.Euler(component.offset_rotation)
		json_resource["offset_rotation"] = blender_rotation_to_stf(offset_rotation.to_quaternion())

	json_resource["filter_avatar"] = component.filter_avatar
	json_resource["filter_world"] = component.filter_world
	json_resource["local_only"] = component.local_only

	collision_tags = []
	for coltag in component.collision_tags:
		if(coltag.tag_name and coltag not in collision_tags):
			collision_tags.append(coltag.tag_name)
	json_resource["collision_tags"] = collision_tags


def vrc_contact_create_resolve_property_path_to_stf_func(blender_property_name: str) -> Callable:
	def handle(context: STF_ExportContext, application_object: Any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
		if(match := re.search(r"^" + blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
			if(component_path := get_component_stf_path_from_collection(application_object, blender_property_name, int(match.groupdict()["component_index"]))):
				return STFPropertyPathPart(component_path + ["enabled"])
		return None
	return handle


def vrc_contact_create_resolve_stf_property_to_blender_func(blender_property_name: str) -> Callable:
	def handle(context: STF_ImportContext, stf_path: list[str], application_object: Any) -> BlenderPropertyPathPart:
		blender_object = context.get_imported_resource(stf_path[0])
		if(component_index := get_component_index(application_object, blender_property_name, blender_object.stf_id)):
			match(stf_path[1]):
				case "enabled":
					return BlenderPropertyPathPart("OBJECT", blender_property_name + "[" + str(component_index) + "].enabled")
		return None
	return handle

