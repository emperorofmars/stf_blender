import bpy
from typing import Callable


class STFPropertyPathPart:
	"""Represents a part of a path to an animatable property in Blender, so that it can be converted to STF"""

	def __init__(
			self,
			stf_path_part: list[str] = [],
			convert_func: Callable[[list[float]], list[float]] = None,
			index_conversion: list[int] = None,
			bake_constraints: bool = False
			):
		self.stf_path_part = stf_path_part
		self.convert_func = convert_func
		self.index_conversion = index_conversion
		self.bake_constraints = bake_constraints

	def __add__(self, other):
		if(other):
			return STFPropertyPathPart(self.stf_path_part + other.stf_path_part, other.convert_func, other.index_conversion, self.bake_constraints | other.bake_constraints)
		else:
			return None


class BlenderPropertyPathPart:
	"""Represents a part of a path to an animatable property in STF, so that it can be converted to Blender"""

	def __init__(
			self,
			slot_type: str = None,
			blender_path: str = "",
			convert_func: Callable[[list[float]], list[float]] = None,
			index_conversion: list[int] = None,
			slot_link_target: bpy.types.Object = None,
			slot_link_property_index: int = 0
			):
		self.slot_type = slot_type
		self.blender_path = blender_path
		self.convert_func = convert_func
		self.index_conversion = index_conversion
		self.slot_link_target = slot_link_target
		self.slot_link_property_index = slot_link_property_index

	def __add__(self, other):
		if(other):
			return BlenderPropertyPathPart(
				other.slot_type,
				self.blender_path + ("." if len(self.blender_path) > 0 and len(other.blender_path) > 0 else "") + other.blender_path,
				other.convert_func,
				other.index_conversion,
				self.slot_link_target,
				max(self.slot_link_property_index, other.slot_link_property_index)
				)
		else:
			return None

