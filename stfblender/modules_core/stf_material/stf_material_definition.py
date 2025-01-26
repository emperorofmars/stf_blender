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
	property_type: bpy.props.StringProperty(name="Type") # type: ignore
	multi_value: bpy.props.BoolProperty(name="Allows Multiple Values", default=False) # type: ignore

	value_property_name: bpy.props.StringProperty() # type: ignore
	value_type: bpy.props.StringProperty() # type: ignore
	values: bpy.props.CollectionProperty(type=STF_Material_Value_Ref) # type: ignore
	active_value_index: bpy.props.IntProperty() # type: ignore


class StringProperty(bpy.types.PropertyGroup):
	value: bpy.props.StringProperty() # type: ignore

class ShaderTarget(bpy.types.PropertyGroup):
	target: bpy.props.StringProperty() # type: ignore
	shaders: bpy.props.CollectionProperty(type=StringProperty) # type: ignore

class STF_Material_Definition(bpy.types.PropertyGroup):
	"""This object merely holds all the meta information for a material"""
	style_hints: bpy.props.CollectionProperty(type=StringProperty, name="Style Hints") # type: ignore
	shader_targets: bpy.props.CollectionProperty(type=ShaderTarget, name="Shader Targets") # type: ignore



def add_property(blender_material: bpy.types.Material, property_type: str, value_module: STF_Material_Value_Module_Base) -> tuple[STF_Material_Property, STF_Material_Value_Ref, STF_Material_Value_Module_Base]:
	prop = blender_material.stf_material_properties.add()
	prop.property_type = property_type
	prop.value_property_name = value_module.property_name
	prop.value_type = value_module.value_type

	value_ref, value = add_value_to_property(blender_material, len(blender_material.stf_material_properties) - 1)
	return prop, value_ref, value


def remove_property(blender_material: bpy.types.Material, index: int):
	property: STF_Material_Property = blender_material.stf_material_properties[index]
	for value_ref in property.values:
		blender_value_collection = getattr(blender_material, property.value_property_name)
		for value_index, value in enumerate(blender_value_collection):
			if(value.value_id == value_ref.value_id):
				blender_value_collection.remove(value_index)
				break
	for property_index, property_candidate in enumerate(blender_material.stf_material_properties):
		if(property_candidate == property):
			blender_material.stf_material_properties.remove(property_index)
			break


def add_value_to_property(blender_material: bpy.types.Material, index: int) -> tuple[STF_Material_Value_Ref, STF_Material_Value_Module_Base]:
	property: STF_Material_Property = blender_material.stf_material_properties[index]
	value_ref = property.values.add()
	max_id = 0
	for value in getattr(blender_material, property.value_property_name):
		if(value.value_id >= max_id): max_id = value.value_id + 1
	value_ref.value_id = max_id
	value = getattr(blender_material, property.value_property_name).add()
	value.value_id = max_id
	return value_ref, value

def remove_property_value(blender_material: bpy.types.Material, index: int):
	property: STF_Material_Property = blender_material.stf_material_properties[index]
	value_ref = property.values[property.active_value_index]
	blender_value_collection = getattr(blender_material, property.value_property_name)
	for value_index, value in enumerate(blender_value_collection):
		if(value.value_id == value_ref.value_id):
			blender_value_collection.remove(value_index)
			break
	property.values.remove(property.active_value_index)


def clear_stf_material(blender_material: bpy.types.Material):
	blender_material.stf_material.style_hints.clear()
	for mat_property in blender_material.stf_material_properties:
		if(hasattr(blender_material, mat_property.value_property_name)):
			getattr(blender_material, mat_property.value_property_name).clear()
	blender_material.stf_material_property_value_refs.clear()
	blender_material.stf_active_material_property_index = 0
	blender_material.stf_material_properties.clear()


def register():
	bpy.types.Material.stf_is_source_of_truth = bpy.props.BoolProperty(name="STF Material Is Source Of Truth", default=False) # type: ignore

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
