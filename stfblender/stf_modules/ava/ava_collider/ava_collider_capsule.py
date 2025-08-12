import bpy
import mathutils

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import ComponentLoadJsonOperatorBase, add_component, export_component_base, import_component_base
from ....utils.trs_utils import blender_rotation_to_stf, blender_translation_to_stf, stf_rotation_to_blender, stf_translation_to_blender


_stf_type = "ava.collider.capsule"
_blender_property_name = "ava_collider_capsule"


class AVA_Collider_Capsule(STF_BlenderComponentBase):
	radius: bpy.props.FloatProperty(name="Radius", default=1) # type: ignore
	height: bpy.props.FloatProperty(name="Height", default=1) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0), subtype="XYZ") # type: ignore
	offset_rotation: bpy.props.FloatVectorProperty(name="Rotation Offset", size=3, default=(0, 0, 0), subtype="EULER") # type: ignore



def _parse_json(component: AVA_Collider_Capsule, json_resource: dict):
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


class AVA_Collider_Capsule_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.ava_collider_capsule_loadjson"
	blender_bone: bpy.props.BoolProperty() # type: ignore

	def get_property(self, context) -> any:
		if(not self.blender_bone):
			return context.object.ava_collider_capsule
		else:
			return context.bone.ava_collider_capsule

	def parse_json(self, context, component: any, json_resource: dict):
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")
		_parse_json(component, json_resource)
		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Collider_Capsule):
	layout.prop(component, "radius")
	layout.prop(component, "height")
	layout.prop(component, "offset_position")
	layout.prop(component, "offset_rotation")

	load_json_button = layout.operator(AVA_Collider_Capsule_LoadJsonOperator.bl_idname)
	load_json_button.blender_bone = type(component.id_data) == bpy.types.Armature
	load_json_button.component_id = component.stf_id


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	_parse_json(component, json_resource)
	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Collider_Capsule, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, application_object)
	ret["radius"] = application_object.radius
	ret["height"] = application_object.height

	offset_position = mathutils.Vector(application_object.offset_position)
	ret["offset_position"] = blender_translation_to_stf(offset_position)

	offset_rotation = mathutils.Euler(application_object.offset_rotation)
	ret["offset_rotation"] = blender_rotation_to_stf(offset_rotation.to_quaternion())
	return ret, application_object.stf_id


class STF_Module_AVA_Collider_Capsule(STF_BlenderComponentModule):
	"""Capsule collider"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["collider.capsule", "collider"]
	understood_application_types = [AVA_Collider_Capsule]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_Collider_Capsule
]


def register():
	bpy.types.Object.ava_collider_capsule = bpy.props.CollectionProperty(type=AVA_Collider_Capsule) # type: ignore
	bpy.types.Bone.ava_collider_capsule = bpy.props.CollectionProperty(type=AVA_Collider_Capsule) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "ava_collider_capsule"):
		del bpy.types.Object.ava_collider_capsule
	if hasattr(bpy.types.Bone, "ava_collider_capsule"):
		del bpy.types.Bone.ava_collider_capsule

