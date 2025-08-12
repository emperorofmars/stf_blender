import bpy
from typing import Callable

from .stf_module import STF_Module
from .stf_module_component import STF_Component_Ref

"""
STF data-resources that aren't natively supported by Blender, similar to components, are stored by the Collection that represents the STF-Prefab.
"""

class STF_Data_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct data-resource in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name") # type: ignore
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component") # type: ignore


class STF_BlenderDataBase(bpy.types.PropertyGroup):
	"""Base class for stf data-resources which are non-native to Blender"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional component name") # type: ignore


class STF_BlenderDataModule(STF_Module):
	"""Extension to STF_Module which also associates a function to draw the data-resources in Blender's UI"""
	blender_property_name: str
	filter: list
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderDataBase) -> None
	draw_component_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Data_Ref, any, any], None]


def register():
	bpy.types.Collection.stf_data_refs = bpy.props.PointerProperty(type=STF_Data_Ref, name="STF Data Refs") # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "stf_data_refs"):
		del bpy.types.Collection.stf_data_refs
