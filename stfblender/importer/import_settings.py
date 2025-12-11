import bpy


class STF_ImportSettings(bpy.types.PropertyGroup):
	import_baked_animations: bpy.props.BoolProperty(name="Import Baked Animations", default=False) # type: ignore

