import bpy
from typing import Any

from ....stfblender_common import STF_ImportContext, STF_ExportContext, STF_TaskSteps, STF_Category, STFReport, STF_DataResourceBase, STF_Handler_Data, STF_Handler_ComponentHolder, STF_Data_Ref, add_resource, export_data_resource_base, get_components_from_data_resource, import_data_resource_base
from ....stfblender_common.helpers import draw_list, poll_valid_animations


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


class Handler_STFEXP_Animation_Blendtree(STF_Handler_Data, STF_Handler_ComponentHolder):
	"""Define a blendtree for animations"""
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	understood_blender_types = [STFEXP_Animation_Blendtree]
	blender_property_name = _blender_property_name

	@staticmethod
	def draw_resource_func(layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_Data_Ref, context_resource: Any, resource: STFEXP_Animation_Blendtree):
		layout.prop(resource, "type")

		if(resource.type == "2d"):
			draw_list(layout, "collection", resource, "animations", _blender_property_name, _draw_func_animation2d)
		else:
			draw_list(layout, "collection", resource, "animations", _blender_property_name, _draw_func_animation1d)

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any | None) -> Any | STFReport:
		resource_ref, resource = add_resource(context.get_root_collection(), _blender_property_name, stf_id, _stf_type)
		import_data_resource_base(resource, json_resource)
		resource.type = json_resource["blendtree_type"]

		def _handle():
			for animation_mapping in json_resource.get("animations"):  # pyright: ignore[reportOptionalIterable]
				mapping: BlendtreeAnimationMapping = resource.animations.add()
				mapping.position[0] = animation_mapping["position"][0]
				if(resource.type == "2d"):
					mapping.position[1] = animation_mapping["position"][1]
				mapping.animation = context.import_resource(json_resource, animation_mapping.get("animation"), STF_Category.DATA)
		context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

		return resource

	@staticmethod
	def export_resource(context: STF_ExportContext, blender_resource: STFEXP_Animation_Blendtree, context_resource: Any | None) -> tuple[dict, str] | STFReport:
		ret = export_data_resource_base(context, _stf_type, blender_resource)
		ret["blendtree_type"] = blender_resource.type

		def _handle():
			animations = []
			for mapping in blender_resource.animations:
				if(mapping.animation):
					anim_id = context.serialize_resource(ret, mapping.animation, stf_category=STF_Category.DATA)
					if(anim_id is not None):
						animations.append({
							"position": mapping.position[:] if blender_resource.type == "2d" else mapping.position[0],
							"animation": anim_id,
						})
			ret["animations"] = animations
		context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

		return ret, blender_resource.stf_id

	get_components = get_components_from_data_resource


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Animation_Blendtree, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
