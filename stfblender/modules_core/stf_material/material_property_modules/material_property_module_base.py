from typing import Callable
import bpy


class Material_Property_Module_Base:
	property_group: str
	priority: int = 0
	from_blender_func: Callable[[bpy.types.Material], bool]
	to_blender_func: Callable[[bpy.types.Material], bool]
	draw_func: Callable[[bpy.types.Material], bool]
