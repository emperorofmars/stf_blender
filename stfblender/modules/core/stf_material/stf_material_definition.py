from typing import Callable
import bpy


class STF_Material_Value_Base(bpy.types.PropertyGroup):
	value_id: bpy.props.IntProperty() # type: ignore


class STF_Material_Value_Module_Base:
	value_type: str
	property_name: str

	# (STF Context, Blender Material, STF Value Json, Blender STF Material Value)
	value_import_func: Callable[[any, bpy.types.Material, any, STF_Material_Value_Base], None]

	# (STF Context, Blender Material, Blender STF Material Value) -> Json Value
	value_export_func: Callable[[any, bpy.types.Material, STF_Material_Value_Base], any]

	draw_func: Callable[[bpy.types.UILayout, bpy.types.Context, bpy.types.Material, STF_Material_Value_Base], None]


class STF_Material_Value_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""References the 'value_id' of the actual value property, whose property-name is unknown by this piece of code."""
	value_id: bpy.props.IntProperty() # type: ignore


class STF_Material_Property(bpy.types.PropertyGroup):
	"""
	A material in STF consists of a dict of properties.
	The property type must be unique within a material.
	A property can have one or more values. Available value types are contained in './stf_blender_material_values'. Maybe these could become hot-loadable at some point.
	"""
	property_type: bpy.props.StringProperty(name="Property ID", description="IDs like `albedo.texture` or `metallic.value`") # type: ignore
	multi_value: bpy.props.BoolProperty(name="Allows Multiple Values", default=False, description="Sometimes you want multiple values. I.e. if you want to have multiple decals.") # type: ignore

	value_property_name: bpy.props.StringProperty() # type: ignore
	value_type: bpy.props.StringProperty() # type: ignore
	values: bpy.props.CollectionProperty(type=STF_Material_Value_Ref) # type: ignore
	active_value_index: bpy.props.IntProperty() # type: ignore


class StringProperty(bpy.types.PropertyGroup):
	value: bpy.props.StringProperty() # type: ignore

class ShaderTarget(bpy.types.PropertyGroup):
	target: bpy.props.StringProperty(name="Target Application") # type: ignore
	shaders: bpy.props.CollectionProperty(type=StringProperty, name="Target Shader") # type: ignore

class STF_Material_Definition(bpy.types.PropertyGroup):
	"""This object merely holds all the meta information for a material"""
	style_hints: bpy.props.CollectionProperty(type=StringProperty, name="Style Hints") # type: ignore
	shader_targets: bpy.props.CollectionProperty(type=ShaderTarget, name="Shader Targets") # type: ignore


def register():
	bpy.types.Material.stf_is_source_of_truth = bpy.props.BoolProperty(name="STF Material Is Source Of Truth", default=False, description="Whether to use the explicit STF material definition, or to convert the Blender material, overwriting any existing STF material properties") # type: ignore

	bpy.types.Material.stf_material = bpy.props.PointerProperty(type=STF_Material_Definition, name="STF Material")
	bpy.types.Material.stf_material_properties = bpy.props.CollectionProperty(type=STF_Material_Property, name="STF Material Properties")
	bpy.types.Material.stf_active_material_property_index = bpy.props.IntProperty()
	bpy.types.Material.stf_material_property_value_refs = bpy.props.CollectionProperty(type=STF_Material_Value_Ref, name="STF Material Values")

def unregister():
	if hasattr(bpy.types.Material, "stf_is_source_of_truth"):
		del bpy.types.Material.stf_is_source_of_truth

	if hasattr(bpy.types.Material, "stf_material"):
		del bpy.types.Material.stf_material
	if hasattr(bpy.types.Material, "stf_material_properties"):
		del bpy.types.Material.stf_material_properties
	if hasattr(bpy.types.Material, "stf_active_material_property_index"):
		del bpy.types.Material.stf_active_material_property_index
	if hasattr(bpy.types.Material, "stf_material_property_values"):
		del bpy.types.Material.stf_material_property_values
