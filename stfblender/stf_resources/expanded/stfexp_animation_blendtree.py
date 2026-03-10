import bpy
from typing import Any

from ...common import STF_ImportContext, STF_ExportContext, STF_TaskSteps, STF_Category, STFReport
from ...common.resource.data import STF_DataResourceBase, STF_Handler_Data, STF_Data_Ref
from ...common.resource.data.data_resource_utils import add_resource, export_data_resource_base, get_components_from_data_resource, import_data_resource_base
from ...common.helpers import draw_list, poll_valid_animations, import_resource, export_resource


_stf_type = "stfexp.animation_blendtree"
_blender_property_name = "stfexp.animation_blendtree"


class BlendtreeAnimationMapping(bpy.types.PropertyGroup):
	position: bpy.props.FloatVectorProperty(name="Position", size=2, default=(0, 0), soft_min=-1, soft_max=1, options=set(), subtype="XYZ") # type: ignore
	animation: bpy.props.PointerProperty(name="Animation", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore

class STFEXP_Animation_Blendtree(STF_DataResourceBase):
	type: bpy.props.EnumProperty(name="Type", items=(("1d", "1D", ""), ("2d", "2D", ""))) # type: ignore
	animations: bpy.props.CollectionProperty(type=BlendtreeAnimationMapping, options=set()) # type: ignore


def _draw_func_animation2d(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box = layout.box()
	row = box.row(align=False)
	row_inner = row.row(align=True)
	row_inner.prop(element, "animation", text="")
	row_inner.prop(element, "position", text="")
	return row

def _draw_func_animation1d(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box = layout.box()
	row = box.row(align=False)
	row_inner = row.row(align=True)
	row_inner.prop(element, "animation", text="")
	row_inner.prop(element, "position", index=0)
	return row


def _draw_resource(layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_Data_Ref, context_object: bpy.types.Collection, resource: STFEXP_Animation_Blendtree):
	layout.prop(resource, "type")

	if(resource.type == "2d"):
		draw_list(layout, "collection", resource, "animations", _blender_property_name, _draw_func_animation2d)
	else:
		draw_list(layout, "collection", resource, "animations", _blender_property_name, _draw_func_animation1d)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: bpy.types.Collection) -> Any | STFReport:
	resource_ref, resource = add_resource(context.get_root_collection(), _blender_property_name, stf_id, _stf_type)
	import_data_resource_base(resource, json_resource)
	resource.type = json_resource["blendtree_type"]

	def _handle():
		for animation_mapping in json_resource.get("animations"):
			mapping: BlendtreeAnimationMapping = resource.animations.add()
			mapping.position[0] = animation_mapping["position"][0]
			if(resource.type == "2d"):
				mapping.position[1] = animation_mapping["position"][1]
			mapping.animation = import_resource(context, json_resource, animation_mapping.get("animation"), STF_Category.DATA)
	context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

	return resource


def _stf_export(context: STF_ExportContext, resource: STFEXP_Animation_Blendtree, context_object: bpy.types.Collection) -> tuple[dict, str] | STFReport:
	ret = export_data_resource_base(context, _stf_type, resource)
	ret["blendtree_type"] = resource.type

	def _handle():
		animations = []
		for mapping in resource.animations:
			if(mapping.animation):
				anim_id = export_resource(context, ret, mapping.animation)
				if(anim_id >= 0):
					animations.append({
						"position": mapping.position[:] if resource.type == "2d" else mapping.position[0],
						"animation": anim_id,
					})
		ret["animations"] = animations
	context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

	return ret, resource.stf_id


class Handler_STFEXP_Animation_Blendtree(STF_Handler_Data):
	"""Define a blendtree for animations"""
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	understood_application_types = [STFEXP_Animation_Blendtree]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	draw_resource_func = _draw_resource
	get_components_func = get_components_from_data_resource


register_stf_handlers = [
	Handler_STFEXP_Animation_Blendtree,
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Animation_Blendtree, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
