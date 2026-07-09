import bpy
from typing import Any, Callable, Protocol

from . import STF_Handler_BlenderNative
from . import PSTF_Component_Ref

"""
STF data-resources that aren't natively supported by Blender, similar to components, are stored by the Collection that represents the STF-Prefab.
"""

class PSTF_Data_Ref(Protocol): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct data-resource in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: str
	stf_id: str
	blender_property_name: str

	id_data: bpy.types.ID | None
	rna_ancestors: Callable[[], list[bpy.types.bpy_struct]]

class PSTF_DataResourceBase(Protocol):
	"""Base class for stf data-resources which are non-native to Blender"""
	stf_id: str
	stf_name: str
	stf_components: list[PSTF_Component_Ref]
	stf_active_component_index: int

	id_data: bpy.types.ID | None
	rna_ancestors: Callable[[], list[bpy.types.bpy_struct]]


class STF_Handler_Data(STF_Handler_BlenderNative, Protocol):
	"""Extension to STF_Module which also associates a function to draw the data-resources in Blender's UI"""

	blender_property_name: str
	"""Blender collection property on which this resource can be added to"""

	draw_resource_func: Callable[[bpy.types.UILayout, bpy.types.Context, PSTF_Data_Ref, Any, Any], None]
	"""
	`def draw_resource_func(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_BlenderDataResourceBase) -> None`
	"""
