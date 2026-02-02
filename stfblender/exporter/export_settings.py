import bpy


class STF_ExportSettings(bpy.types.PropertyGroup):
	stf_animation_bake_constraints: bpy.props.BoolProperty(name="Animations Bake Constraints", default=True, description="Bake animations that change values indirectly with constraints") # type: ignore
	stf_animation_preserve_baked: bpy.props.BoolProperty(name="Preserve Baked Animations", default=False, description="Don't remove baked animations after export") # type: ignore

