import bpy
import re
from typing import Callable

from ....base.stf_task_steps import STF_TaskSteps
from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ....utils.animation_conversion_utils import get_component_index, get_component_stf_path, get_component_stf_path_from_collection
from ....base.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf
from ....base.blender_grr.stf_node_path_component_selector import NodePathComponentSelector, draw_node_path_component_selector, node_path_component_selector_from_stf, node_path_component_selector_to_stf
from ....utils.helpers import create_add_button, create_remove_button
from ....utils import trs_utils


_stf_type = "dev.vrm.springbone"
_blender_property_name = "dev_vrm_springbone"

# todo: this is quite jank, make this able to select the object/armature->bone/component etc..
class VRM_Springbone(STF_BlenderComponentBase):
	stiffness: bpy.props.FloatProperty(default=1, min=0, soft_max=4, precision=2, name="Stiffness Force", description="The resilience of the swaying object (the power of returning to the initial pose)") # type: ignore
	gravityPower: bpy.props.FloatProperty(min=0, soft_max=1, precision=2, name="Gravity Power", description="The strength of gravity") # type: ignore
	gravityDir: bpy.props.FloatVectorProperty(default=(0, 0, -1), subtype="XYZ", soft_min=-1, soft_max=1, precision=2, name="Gravity Direction", description="The direction of gravity. Set (0, 0, -1) for simulating the gravity. Set (1, 0, 0) for simulating the wind") # type: ignore
	dragForce: bpy.props.FloatProperty(default=0.4, min=0, max=1, precision=2, name="Drag Force", description="The resistance (deceleration) of automatic animation") # type: ignore
	center: bpy.props.PointerProperty(type=NodePathSelector, name="Center", description="The reference point of a swaying object can be set at any location except the origin. When implementing UI moving with warp, the parent node to move with warp can be specified if you don't want to make the object swaying with warp movement") # type: ignore
	hitRadius: bpy.props.FloatProperty(default=0.02, min=0, soft_max=10, precision=2, unit="LENGTH", name="Hit Radius", description="The radius of the sphere used for the collision detection with colliders") # type: ignore
	colliders: bpy.props.CollectionProperty(type=NodePathComponentSelector, name="Colliders", description="Specify the of the collider components for collisions with swaying objects", options=set()) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRM_Springbone):
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
	create_add_button(row, "bone" if type(component.id_data) == bpy.types.Armature else "object", _blender_property_name, component.stf_id, "colliders")
	box.separator(factor=1)
	for index, collider in enumerate(component.colliders):
		if(index > 0):
			box.separator(factor=1, type="LINE")
		row = box.row(align=True)
		col = row.column(align=True)
		col.use_property_split = True
		draw_node_path_component_selector(col, collider)
		create_remove_button(row, "bone" if type(component.id_data) == bpy.types.Armature else "object", _blender_property_name, component.stf_id, "colliders", index)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, context_object)

	_get_component = preserve_component_reference(component, context_object)
	def _handle():
		component = _get_component()
		for collider_path in json_resource.get("colliders", []):
			new_collider = component.colliders.add()
			node_path_component_selector_from_stf(context, json_resource, collider_path, new_collider)
		if("center" in json_resource):
			node_path_selector_from_stf(context, json_resource, json_resource["center"], component.center)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, component: VRM_Springbone, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["stiffness"] = component.stiffness
	ret["gravityPower"] = component.gravityPower
	ret["gravityDir"] = trs_utils.blender_translation_to_stf(component.gravityDir)
	ret["dragForce"] = component.dragForce
	ret["hitRadius"] = component.hitRadius

	_get_component = preserve_component_reference(component, context_object)
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

	return ret, component.stf_id


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[list[float]], list[float]], list[int]]:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return component_path + ["enabled"], None, None
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	if(component_index := get_component_index(application_object, _blender_property_name, blender_object.stf_id)):
		match(stf_path[1]):
			case "enabled":
				return None, 0, "OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled", None, None
	return None


"""Module definition"""

class STF_Module_VRM_Springbone(STF_BlenderComponentModule):
	"""Represents a `VRM Springbone`"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["secondary_motion"]
	understood_application_types = [VRM_Springbone]
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


register_stf_modules = [
	STF_Module_VRM_Springbone
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=VRM_Springbone))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=VRM_Springbone))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
