import bpy
from typing import Any, Callable, Protocol

from ..stf_handler_base import STF_HandlerBase
from .stf_data_resource import STF_Data_Ref

"""
STF data-resources that aren't natively supported by Blender, similar to components, are stored by the Collection that represents the STF-Prefab.
"""

__all__ = ["STF_Handler_Data"]

class STF_Handler_Data(STF_HandlerBase, Protocol):
	"""Extension to STF_Module which also associates a function to draw the data-resources in Blender's UI"""

	blender_property_name: str
	"""Blender collection property on which this resource can be added to"""

	draw_resource_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Data_Ref, Any, Any], None]
	"""
	`def draw_resource_func(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_BlenderDataResourceBase) -> None`
	"""
