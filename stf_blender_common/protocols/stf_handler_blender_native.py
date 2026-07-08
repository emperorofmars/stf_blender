from typing import Protocol

from .stf_handler_base import STF_HandlerBase

class STF_Handler_BlenderNative(STF_HandlerBase, Protocol):
	"""Represents functionality to import and export a Blender-native resource"""

