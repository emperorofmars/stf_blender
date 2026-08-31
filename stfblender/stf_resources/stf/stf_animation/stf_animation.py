from typing import Any
import bpy

from .....stfblender_common import STF_Category, STF_ImportContext, STF_ExportContext, STF_Handler_ComponentHolder, STF_Handler_BlenderNative, STFReport, get_components_from_object
from .....stfblender_common.helpers import draw_slot_link_warning
from .....stfblender_common.slot_link import ActionSlotLink, get_slot_link_data_model_version, get_slot_link_version
from .stf_animation_bake import STFBakeAnimationOperator
from .stf_animation_common import stf_animation_type
from .stf_animation_export import stf_animation_export
from .stf_animation_import import stf_animation_import
from .stf_animation_ops import STFAddAnimationComponentOperator, STFEditAnimationComponentIdOperator, STFRemoveAnimationComponentOperator, STFSetAnimationIDOperator


class STF_Animation(bpy.types.PropertyGroup):
	exclude: bpy.props.BoolProperty(name="Exclude from STF export", default=False, options=set())
	fps_override: bpy.props.BoolProperty(name="FPS Override", default=False, options=set())
	fps: bpy.props.FloatProperty(name="FPS", default=30, options=set())
	is_baked_from: bpy.props.PointerProperty(name="Is Baked From", type=bpy.types.Action)
	constraint_bake: bpy.props.EnumProperty(name="Constraint-Baking", items=(("auto", "Automatic", ""), ("bake", "Bake", ""), ("nobake", "Don't Bake", "")), default="auto")


class Handler_STF_Animation(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = stf_animation_type
	stf_category = STF_Category.DATA
	like_types = ["animation"]
	understood_blender_types = [bpy.types.Action]
	priority = 1
	operator_set_stf_id = STFSetAnimationIDOperator.bl_idname

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, blender_resource: tuple[bpy.types.Object, bpy.types.Mesh]) -> None:
		layout.use_property_split = True

		if(not hasattr(bpy.types.Action, "slot_link")):
			draw_slot_link_warning(layout)
			return

		if(context.active_action.stf_animation.is_baked_from):
			row_readonly =  layout.row()
			row_readonly.enabled = False
			row_readonly.prop(context.active_action.stf_animation, "is_baked_from")

		layout.prop(context.active_action.stf_animation, "exclude")
		if(context.active_action.stf_animation.exclude):
			return

		if(not context.active_action.stf_animation.is_baked_from):
			layout.separator(factor=2, type="SPACE")

			layout.prop(context.active_action.stf_animation, "constraint_bake")
			if(context.active_action.stf_animation.constraint_bake != "nobake"):
				layout.operator(STFBakeAnimationOperator.bl_idname)

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		return stf_animation_import(context, json_resource, stf_id, context_resource)

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: Any, context_resource: Any) -> tuple[dict, str] | STFReport:
		return stf_animation_export(context, blender_resource, context_resource)

	@classmethod
	def can_handle_stf_resource_type(cls) -> int:
		return 1 if get_slot_link_version() is not None else -1

	@classmethod
	def can_handle_blender_resource(cls, blender_animation: bpy.types.Action) -> int:
		slot_link_version = get_slot_link_version()
		slot_link_data_model_version = get_slot_link_data_model_version()
		if(slot_link_version == None or slot_link_data_model_version == None or not hasattr(blender_animation, "slot_link")):
			return -1

		if(blender_animation.stf_animation.exclude): return None # pyright: ignore[reportReturnType]
		if(blender_animation.is_action_legacy):
			return -1

		action_slot_link: ActionSlotLink = blender_animation.slot_link
		for slot_link in action_slot_link.links:
			if(slot_link_data_model_version[0] == 0 and slot_link_data_model_version[1] < 2 and slot_link.target):
				break
			elif(len(slot_link.targets) > 0):
				break
		else:
			return -1

		return 10

	get_components = get_components_from_object
	operator_component_add = STFAddAnimationComponentOperator.bl_idname
	operator_component_remove = STFRemoveAnimationComponentOperator.bl_idname
	operator_component_edit = STFEditAnimationComponentIdOperator.bl_idname


def register():
	bpy.types.Action.stf_animation = bpy.props.PointerProperty(type=STF_Animation, options=set())

def unregister():
	if hasattr(bpy.types.Action, "stf_animation"):
		del bpy.types.Action.stf_animation
