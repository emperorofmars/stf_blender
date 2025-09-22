import bpy

from .stf_animation_common import *
from .stf_animation_export import stf_animation_export
from .stf_animation_import import stf_animation_import
from ....base.stf_module import STF_Module
from ....utils.component_utils import get_components_from_object
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister


_stf_type = stf_animation_type


class STF_Animation(bpy.types.PropertyGroup):
	exclude: bpy.props.BoolProperty(name="Exclude from STF export", default=False) # type: ignore
	bake: bpy.props.BoolProperty(name="Bake Animation on Export", default=True) # type: ignore
	fps_override: bpy.props.BoolProperty(name="FPS Override", default=False) # type: ignore
	fps: bpy.props.FloatProperty(name="FPS", default=30) # type: ignore



class STF_Module_STF_Animation(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["animation"]
	understood_application_types = [bpy.types.Action]
	import_func = stf_animation_import
	export_func = stf_animation_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Animation
]


def register():
	boilerplate_register(bpy.types.Action, "data")
	bpy.types.Action.stf_animation = bpy.props.PointerProperty(type=STF_Animation)

def unregister():
	if hasattr(bpy.types.Action, "stf_animation"):
		del bpy.types.Action.stf_animation
	boilerplate_unregister(bpy.types.Action, "data")
