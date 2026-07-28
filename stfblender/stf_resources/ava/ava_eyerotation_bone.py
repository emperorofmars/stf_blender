import bpy
import math
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base


class AVA_EyeRotation_Bone(STF_ComponentResourceBase):
	limit_up: bpy.props.FloatProperty(name="Up", subtype="ANGLE", default=math.radians(15), options=set(), soft_min=0, soft_max=math.radians(60))
	limit_down: bpy.props.FloatProperty(name="Down", subtype="ANGLE", default=math.radians(12), options=set(), soft_min=0, soft_max=math.radians(60))
	limit_in: bpy.props.FloatProperty(name="In", subtype="ANGLE", default=math.radians(15), options=set(), soft_min=0, soft_max=math.radians(60))
	limit_out: bpy.props.FloatProperty(name="Out", subtype="ANGLE", default=math.radians(16), options=set(), soft_min=0, soft_max=math.radians(60))


class Handler_AVA_EyeRotation_Bone(STF_Handler_Component):
	"""Define limits to eyebone rotations"""
	stf_type = "ava.eye_rotation.bone"
	stf_category = STF_Category.COMPONENT
	like_types = []
	understood_blender_types = [AVA_EyeRotation_Bone]
	blender_property_name = "ava_eye_rotation_bone"
	single = True
	filter = [bpy.types.Armature]
	pretty_name_template = "Eye-Rotation Limits"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: AVA_EyeRotation_Bone):
		layout.use_property_split = True
		col = layout.column(align=True)
		col.prop(component, "limit_up")
		col.prop(component, "limit_down")
		col.prop(component, "limit_in")
		col.prop(component, "limit_out")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		component.limit_up = json_resource.get("up", math.radians(15))
		component.limit_down = json_resource.get("down", math.radians(12))
		component.limit_in = json_resource.get("in", math.radians(15))
		component.limit_out = json_resource.get("out", math.radians(16))

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: AVA_EyeRotation_Bone, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		ret["up"] = component.limit_up
		ret["down"] = component.limit_down
		ret["in"] = component.limit_in
		ret["out"] = component.limit_out
		return ret, component.stf_id


def register():
	setattr(bpy.types.Armature, Handler_AVA_EyeRotation_Bone.blender_property_name, bpy.props.CollectionProperty(type=AVA_EyeRotation_Bone, options=set()))

def unregister():
	if hasattr(bpy.types.Armature, Handler_AVA_EyeRotation_Bone.blender_property_name):
		delattr(bpy.types.Armature, Handler_AVA_EyeRotation_Bone.blender_property_name)
