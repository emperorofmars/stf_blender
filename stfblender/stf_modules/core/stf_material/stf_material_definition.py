from typing import Callable
import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....base.property_path_part import BlenderPropertyPathPart, STFPropertyPathPart


class STF_Material_Value_Base(bpy.types.PropertyGroup):
	value_id: bpy.props.IntProperty(options=set()) # type: ignore


class STF_Material_Value_Module_Base:
	value_type: str
	property_name: str

	# (STF Context, Blender Material, STF Value Json, Blender STF Material Value)
	value_import_func: Callable[[any, bpy.types.Material, any, STF_Material_Value_Base], None]

	# (STF Context, Blender Material, Blender STF Material Value) -> Json Value
	value_export_func: Callable[[any, bpy.types.Material, STF_Material_Value_Base], any]

	# Animation import export
	resolve_property_path_to_stf_func: Callable[[STF_ExportContext, str, STF_Material_Value_Base], STFPropertyPathPart]
	resolve_stf_property_to_blender_func: Callable[[STF_ImportContext, list[str]], BlenderPropertyPathPart]

	draw_func: Callable[[bpy.types.UILayout, bpy.types.Context, bpy.types.Material, STF_Material_Value_Base], None]


class STF_Material_Value_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""References the 'value_id' of the actual value property, whose property-name is unknown by this piece of code."""
	value_id: bpy.props.IntProperty(options=set()) # type: ignore


class STF_Material_Property(bpy.types.PropertyGroup):
	"""
	A material in STF consists of a dict of properties.
	The property type must be unique within a material.
	A property can have one or more values. Available value types are contained in './stf_blender_material_values'. Maybe these could become hot-loadable at some point.
	"""
	property_type: bpy.props.StringProperty(name="Property ID", description="IDs like `albedo.texture` or `metallic.value`", options=set()) # type: ignore
	multi_value: bpy.props.BoolProperty(name="Allows Multiple Values", default=False, description="Sometimes you want multiple values. I.e. if you want to have multiple decals.", options=set()) # type: ignore

	value_property_name: bpy.props.StringProperty(options=set()) # type: ignore
	value_type: bpy.props.StringProperty(options=set()) # type: ignore
	values: bpy.props.CollectionProperty(type=STF_Material_Value_Ref, options=set()) # type: ignore
	active_value_index: bpy.props.IntProperty(options=set()) # type: ignore


class StringProperty(bpy.types.PropertyGroup):
	value: bpy.props.StringProperty(options=set()) # type: ignore

class ShaderTarget(bpy.types.PropertyGroup):
	target: bpy.props.StringProperty(name="Target Application", options=set()) # type: ignore
	shaders: bpy.props.CollectionProperty(type=StringProperty, name="Target Shader", options=set()) # type: ignore

class STF_Material_Definition(bpy.types.PropertyGroup):
	"""This object merely holds all the meta information for a material"""
	stf_is_source_of_truth: bpy.props.BoolProperty(name="STF Material Is Source Of Truth", default=False, description="Whether to use the explicit STF material definition, or to convert the Blender material, overwriting any existing STF material properties", options=set()) # type: ignore
	style_hints: bpy.props.CollectionProperty(type=StringProperty, name="Style Hints", options=set()) # type: ignore
	shader_targets: bpy.props.CollectionProperty(type=ShaderTarget, name="Shader Targets", options=set()) # type: ignore
	properties: bpy.props.CollectionProperty(type=STF_Material_Property, name="STF Material Properties", options=set()) # type: ignore
	active_property_index: bpy.props.IntProperty(options=set()) # type: ignore


def register():
	bpy.types.Material.stf_material = bpy.props.PointerProperty(type=STF_Material_Definition, name="STF Material", options=set())

def unregister():
	if hasattr(bpy.types.Material, "stf_material"):
		del bpy.types.Material.stf_material
