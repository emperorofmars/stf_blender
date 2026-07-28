import bpy
import re
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Component_Ref, ComponentLoadJsonOperatorBase, STFReport, add_component, export_component_base, import_component_base, preserve_component_reference
from .....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from .....stfblender_common.utils import trs_utils
from .....stfblender_common.helpers import create_add_button, create_remove_button
from .....stfblender_common.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf
from .....stfblender_common.blender_grr.stf_node_path_component_selector import NodePathComponentSelector, draw_node_path_component_selector, node_path_component_selector_from_stf, node_path_component_selector_to_stf


_stf_type = "dev.vrm.springbone"
_blender_property_name = "dev_vrm_springbone"


class VRM_Springbone(STF_ComponentResourceBase):
	stiffness: bpy.props.FloatProperty(default=1, min=0, soft_max=4, precision=2, name="Stiffness Force", description="The resilience of the swaying object (the power of returning to the initial pose)")
	gravityPower: bpy.props.FloatProperty(min=0, soft_max=1, precision=2, name="Gravity Power", description="The strength of gravity")
	gravityDir: bpy.props.FloatVectorProperty(default=(0, 0, -1), subtype="XYZ", soft_min=-1, soft_max=1, precision=2, name="Gravity Direction", description="The direction of gravity. Set (0, 0, -1) for simulating the gravity. Set (1, 0, 0) for simulating the wind")
	dragForce: bpy.props.FloatProperty(default=0.4, min=0, max=1, precision=2, name="Drag Force", description="The resistance (deceleration) of automatic animation")
	center: bpy.props.PointerProperty(type=NodePathSelector, name="Center", description="The reference point of a swaying object can be set at any location except the origin. When implementing UI moving with warp, the parent node to move with warp can be specified if you don't want to make the object swaying with warp movement")
	hitRadius: bpy.props.FloatProperty(default=0.02, min=0, soft_max=10, precision=2, unit="LENGTH", name="Hit Radius", description="The radius of the sphere used for the collision detection with colliders")
	colliders: bpy.props.CollectionProperty(type=NodePathComponentSelector, name="Colliders", description="Specify the of the collider components for collisions with swaying objects", options=set())


class VRM_Springbone_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.dev_vrm_springbone_loadjson"
	blender_bone: bpy.props.BoolProperty()

	def get_property(self, context) -> Any:
		if(not self.blender_bone):
			return context.object.dev_vrm_springbone
		else:
			return context.bone.dev_vrm_springbone

	def parse_json(self, context: bpy.types.Context, component: Any, json_resource: dict):
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")

		if("stiffness" in json_resource): component.stiffness = json_resource["stiffness"]
		if("gravityPower" in json_resource): component.gravityPower = json_resource["gravityPower"]
		if("gravityDir" in json_resource): component.gravityDir = trs_utils.stf_translation_to_blender(json_resource["gravityDir"])
		if("dragForce" in json_resource): component.dragForce = json_resource["dragForce"]
		if("hitRadius" in json_resource): component.hitRadius = json_resource["hitRadius"]


class Handler_VRM_Springbone(STF_Handler_BoneComponent):
	"""Represents a `VRM Springbone`"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["secondary_motion"]
	understood_blender_types = [VRM_Springbone]
	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "VRM Springbone"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: Any) -> None:
		layout.use_property_split = True
		col = layout.column()
		col.prop(component, "stiffness", slider=True)
		col.prop(component, "gravityPower", slider=True)
		col.prop(component, "gravityDir")
		col.prop(component, "dragForce", slider=True)
		draw_node_path_selector(col, component.center, text="Center")
		col.prop(component, "hitRadius", slider=True)

		layout.separator(factor=1)

		box = layout.box().column(align=True)
		row = box.row()
		row.label(text="Colliders")
		create_add_button(row, "bone" if type(component.id_data) is bpy.types.Armature else "object", cls.blender_property_name, component.stf_id, "colliders")
		box.separator(factor=1)
		for index, collider in enumerate(component.colliders):
			if(index > 0):
				box.separator(factor=1, type="LINE")
			row = box.row(align=True)
			col = row.column(align=True)
			col.use_property_split = True
			draw_node_path_component_selector(col, collider)
			create_remove_button(row, "bone" if type(component.id_data) is bpy.types.Armature else "object", cls.blender_property_name, component.stf_id, "colliders", index)

		load_json_button = layout.operator(VRM_Springbone_LoadJsonOperator.bl_idname)
		load_json_button.blender_bone = type(component.id_data) is bpy.types.Armature
		load_json_button.component_id = component.stf_id

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any | None) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, _stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		if("stiffness" in json_resource): component.stiffness = json_resource["stiffness"]
		if("gravityPower" in json_resource): component.gravityPower = json_resource["gravityPower"]
		if("gravityDir" in json_resource): component.gravityDir = trs_utils.stf_translation_to_blender(json_resource["gravityDir"])
		if("dragForce" in json_resource): component.dragForce = json_resource["dragForce"]
		if("hitRadius" in json_resource): component.hitRadius = json_resource["hitRadius"]

		_get_component = preserve_component_reference(component, cls.blender_property_name, context_resource)
		def _handle():
			component = _get_component()
			for collider_path in json_resource.get("colliders", []):
				new_collider = component.colliders.add()
				node_path_component_selector_from_stf(context, json_resource, collider_path, new_collider)
			if("center" in json_resource):
				node_path_selector_from_stf(context, json_resource, json_resource["center"], component.center)
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Any, context_resource: Any | None) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, blender_resource, cls.blender_property_name, context_resource)
		ret["stiffness"] = blender_resource.stiffness
		ret["gravityPower"] = blender_resource.gravityPower
		ret["gravityDir"] = trs_utils.blender_translation_to_stf(blender_resource.gravityDir)
		ret["dragForce"] = blender_resource.dragForce
		ret["hitRadius"] = blender_resource.hitRadius

		_get_component = preserve_component_reference(blender_resource, cls.blender_property_name, context_resource)
		def _handle():
			component = _get_component()
			colliders = []
			for collider in component.colliders:
				if(collider_ret := node_path_component_selector_to_stf(context, collider, ret)):
					colliders.append(collider_ret)
			if(len(colliders)):
				ret["colliders"] = colliders
			if(component.center):
				if(center_ret := node_path_selector_to_stf(context, component.center, ret)):
					ret["center"] = center_ret
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

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
		blender_object = context.get_imported_resource(stf_property_path[0])
		component_index = get_component_index(blender_resource, cls.blender_property_name, blender_object.stf_id)
		if(component_index is not None):
			match(stf_property_path[1]):
				case "enabled":
					return BlenderPropertyPathPart("OBJECT", cls.blender_property_name + "[" + str(component_index) + "].enabled")
		return None


def register():
	setattr(bpy.types.Object, Handler_VRM_Springbone.blender_property_name, bpy.props.CollectionProperty(type=VRM_Springbone))
	setattr(bpy.types.Bone, Handler_VRM_Springbone.blender_property_name, bpy.props.CollectionProperty(type=VRM_Springbone))

def unregister():
	if hasattr(bpy.types.Object, Handler_VRM_Springbone.blender_property_name):
		delattr(bpy.types.Object, Handler_VRM_Springbone.blender_property_name)
	if hasattr(bpy.types.Bone, Handler_VRM_Springbone.blender_property_name):
		delattr(bpy.types.Bone, Handler_VRM_Springbone.blender_property_name)
