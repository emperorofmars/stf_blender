import bpy
import mathutils

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.helpers import create_add_button, create_remove_button
from ....base.stf_module_component import STF_BlenderComponentBase, STF_Component_Ref
from ....utils.trs_utils import blender_rotation_to_stf, blender_translation_to_stf, stf_rotation_to_blender, stf_translation_to_blender


class CollisionTag(bpy.types.PropertyGroup):
	tag_name: bpy.props.StringProperty(name="Tag", options=set()) # type: ignore


class VRC_ContactBase(STF_BlenderComponentBase):
	shape: bpy.props.EnumProperty(name="Shape", items=(("sphere", "Sphere", ""), ("capsule", "Capsule", "")), default="sphere", options=set()) # type: ignore
	radius: bpy.props.FloatProperty(name="Radius", default=1, min=0) # type: ignore
	height: bpy.props.FloatProperty(name="Height", default=1, min=0) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ") # type: ignore
	offset_rotation: bpy.props.FloatVectorProperty(name="Rotation Offset", size=3, default=(0, 0, 0), subtype="EULER") # type: ignore
	filter_component_types_avatar: bpy.props.BoolProperty(name="Avatar", default=False, options=set()) # type: ignore
	filter_component_types_world: bpy.props.BoolProperty(name="World", default=False, options=set()) # type: ignore
	filter_local_only: bpy.props.BoolProperty(name="Local Only", default=False, options=set()) # type: ignore
	collision_tags: bpy.props.CollectionProperty(name="Collision Tags", type=CollisionTag, options=set()) # type: ignore


def vrc_contact_draw_base(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_ContactBase, blender_property_name: str):
	col = layout.column(align=True)
	col.prop(component, "shape")
	col.prop(component, "radius")
	if(component.shape == "capsule"):
		col.prop(component, "height")

	layout.prop(component, "offset_position")
	if(component.shape == "capsule"):
		layout.prop(component, "offset_rotation")

	row = layout.row(align=True, heading="Filter")
	row.prop(component, "filter_component_types_avatar", toggle=True)
	row.prop(component, "filter_component_types_world", toggle=True)
	row.prop(component, "filter_local_only", toggle=True)

	box = layout.box()
	box.label(text="Collision Tags")
	col = box.column(align=True)
	for index_coltag, coltag in enumerate(component.collision_tags):
		row = col.row(align=True)
		row.prop(coltag, "tag_name")
		create_remove_button(row, "object" if type(component.id_data) == bpy.types.Object else "bone", blender_property_name, component.stf_id, "collision_tags", index_coltag)
	create_add_button(box, "object" if type(component.id_data) == bpy.types.Object else "bone", blender_property_name, component.stf_id, "collision_tags")


def vrc_contact_import_base(context: STF_ImportContext, component: VRC_ContactBase, json_resource: dict):
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

	component.filter_component_types_avatar = json_resource.get("filter_avatar", False)
	component.filter_component_types_world = json_resource.get("filter_world", False)
	component.filter_local_only = json_resource.get("filter_local_only", False)

	for coltag in json_resource.get("collision_tags", []):
		new_tag = component.collision_tags.add()
		new_tag.name = coltag
		new_tag.tag_name = coltag


def vrc_contact_export_base(context: STF_ExportContext, component: VRC_ContactBase, context_object: any, json_resource: dict):
	json_resource["shape"] = component.shape
	json_resource["radius"] = component.radius
	if(component.shape == "capsule"):
		json_resource["height"] = component.height
	offset_position = mathutils.Vector(component.offset_position)
	json_resource["offset_position"] = blender_translation_to_stf(offset_position)
	if(component.shape == "capsule"):
		offset_rotation = mathutils.Euler(component.offset_rotation)
		json_resource["offset_rotation"] = blender_rotation_to_stf(offset_rotation.to_quaternion())

	json_resource["filter_avatar"] = component.filter_component_types_avatar
	json_resource["filter_world"] = component.filter_component_types_world
	json_resource["filter_local_only"] = component.filter_local_only

	collision_tags = []
	for coltag in component.collision_tags:
		if(coltag.tag_name and coltag not in collision_tags):
			collision_tags.append(coltag.tag_name)
	json_resource["collision_tags"] = collision_tags
