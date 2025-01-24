import bpy

from .stf_blender_material_values import blender_material_value_modules

def _build_stf_material_value_modules_enum(self, context):
	return [((mat_module.value_type, mat_module.value_type, "")) for mat_module in blender_material_value_modules]


def register():
	bpy.types.Scene.stf_material_value_modules = bpy.props.EnumProperty(
		items=_build_stf_material_value_modules_enum,
		name="STF Material Value Modules",
		description="Default & hot-loaded STF Material-Property-Value Modules",
		options={"SKIP_SAVE"},
		default=0
	)

def unregister():
	if hasattr(bpy.types.Scene, "stf_material_value_modules"):
		del bpy.types.Scene.stf_material_value_modules
