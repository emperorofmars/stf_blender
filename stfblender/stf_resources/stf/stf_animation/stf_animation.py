import bpy

from .....stfblender_common import STF_Category, STF_Handler_ComponentHolder, STF_Handler_BlenderNative, boilerplate_register, boilerplate_unregister, get_components_from_object
from .stf_animation_common import *
from .stf_animation_export import stf_animation_export
from .stf_animation_import import stf_animation_import
from .stf_animation_ui import STFAddAnimationComponentOperator, STFEditAnimationComponentIdOperator, STFRemoveAnimationComponentOperator, STFSetAnimationIDOperator, draw_animation_ui


_stf_type = stf_animation_type


class STF_Animation(bpy.types.PropertyGroup):
	exclude: bpy.props.BoolProperty(name="Exclude from STF export", default=False, options=set()) # type: ignore
	fps_override: bpy.props.BoolProperty(name="FPS Override", default=False, options=set()) # type: ignore
	fps: bpy.props.FloatProperty(name="FPS", default=30, options=set()) # type: ignore
	is_baked_from: bpy.props.PointerProperty(name="Is Baked From", type=bpy.types.Action) # type: ignore
	constraint_bake: bpy.props.EnumProperty(name="Constraint-Baking", items=(("auto", "Automatic", ""), ("bake", "Bake", ""), ("nobake", "Don't Bake", "")), default="auto") # type: ignore


class Handler_STF_Animation(STF_Handler_BlenderNative, STF_Handler_ComponentHolder):
	stf_type = _stf_type
	stf_category = STF_Category.DATA
	like_types = ["animation"]
	understood_application_types = [bpy.types.Action]
	import_func = stf_animation_import
	export_func = stf_animation_export
	operator_set_stf_id = STFSetAnimationIDOperator.bl_idname
	draw = draw_animation_ui

	get_components_func = get_components_from_object
	operator_component_add = STFAddAnimationComponentOperator.bl_idname
	operator_component_remove = STFRemoveAnimationComponentOperator.bl_idname
	operator_component_edit = STFEditAnimationComponentIdOperator.bl_idname


register_stf_handlers = [
	Handler_STF_Animation
]


def register():
	boilerplate_register(bpy.types.Action)
	bpy.types.Action.stf_animation = bpy.props.PointerProperty(type=STF_Animation, options=set())

def unregister():
	if hasattr(bpy.types.Action, "stf_animation"):
		del bpy.types.Action.stf_animation
	boilerplate_unregister(bpy.types.Action)
