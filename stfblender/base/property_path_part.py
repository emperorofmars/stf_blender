from typing import Callable


class STFPropertyPathPart:
	"""Represents a part of a path to an animatable property in Blender, so that it can be converted to STF"""

	def __init__(
			self,
			stf_path_part: list[str] = [],
			convert_func: Callable[[list[float]], list[float]] = None,
			index_conversion: list[int] = None,
			constraints: bool = False
			):
		self.stf_path_part = stf_path_part
		self.convert_func = convert_func
		self.index_conversion = index_conversion
		self.constraints = constraints

	def __add__(self, other):
		if(other):
			return STFPropertyPathPart(self.stf_path_part + other.stf_path_part, other.convert_func, other.index_conversion, self.constraints | other.constraints)
		else:
			return None
