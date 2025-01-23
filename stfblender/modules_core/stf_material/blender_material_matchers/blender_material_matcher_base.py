from typing import Callable
import bpy


class Blender_Material_Property_Matcher_Module_Base:
	property_name: str
	priority: int = 0
	match_func: Callable[[bpy.types.Material], bool]
