from typing import Callable
import bpy


class StringProperty(bpy.types.PropertyGroup):
	value: bpy.props.StringProperty() # type: ignore

class ShaderTarget(bpy.types.PropertyGroup):
	target: bpy.props.StringProperty() # type: ignore
	shaders: bpy.props.CollectionProperty(type=StringProperty) # type: ignore


class STF_Material_Value_Base(bpy.types.PropertyGroup):
	value_id: bpy.props.IntProperty() # type: ignore


class STF_Blender_Material_Value_Module_Base:
	property_name: str

	# (STF Context, Blender Material, STF Value Json)
	value_import_func: Callable[[any, dict, bpy.types.Material], None]

	# (STF Context, Blender Material, Blender STF Material Value) -> Json Value
	value_export_func: Callable[[any, bpy.types.Material, STF_Material_Value_Base], any]

	draw_func: Callable[[bpy.types.UILayout, bpy.types.Context, bpy.types.Material, STF_Material_Value_Base], None]


class STF_Material_Value_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	value_id: bpy.props.IntProperty() # type: ignore


class STF_Material_Property(bpy.types.PropertyGroup):
	property_type: bpy.props.StringProperty(name="Type") # type: ignore
	value_property_name: bpy.props.StringProperty(name="Type") # type: ignore
	values: bpy.props.CollectionProperty(type=STF_Material_Value_Ref, name="Value(s)") # type: ignore
	multi_value: bpy.props.BoolProperty(name="Allows Multiple Values", default=False) # type: ignore
	active_value_index: bpy.props.IntProperty() # type: ignore


class STF_Material_Definition(bpy.types.PropertyGroup):
	style_hints: bpy.props.CollectionProperty(type=StringProperty, name="Style Hints") # type: ignore
	shader_targets: bpy.props.CollectionProperty(type=ShaderTarget, name="Shader Targets") # type: ignore



def add_property(blender_material: bpy.types.Material, property_type: str, value_module: STF_Blender_Material_Value_Module_Base) -> tuple[STF_Material_Property, STF_Material_Value_Ref, STF_Blender_Material_Value_Module_Base]:
	prop = blender_material.stf_material_properties.add()
	prop.property_type = property_type
	prop.value_property_name = value_module.property_name

	value_ref, value = add_value_to_property(blender_material, prop)
	return prop, value_ref, value


def add_value_to_property(blender_material: bpy.types.Material, property: STF_Material_Property) -> tuple[STF_Material_Value_Ref, STF_Blender_Material_Value_Module_Base]:
	value_ref = property.values.add()
	max_id = 0
	for value in getattr(blender_material, property.value_property_name):
		if(value.value_id > max_id): max_id = value.value_id + 1
	value_ref.value_id = max_id
	value = getattr(blender_material, property.value_property_name).add()
	value.value_id = max_id
	return value_ref, value

# TODO remove and move value



def register():
	bpy.types.Material.stf_is_source_of_truth = bpy.props.BoolProperty(name="STF Material Is Source Of Truth", default=False) # type: ignore

	bpy.types.Material.stf_material = bpy.props.PointerProperty(type=STF_Material_Definition, name="STF Material")
	bpy.types.Material.stf_material_properties = bpy.props.CollectionProperty(type=STF_Material_Property, name="STF Material Properties")
	bpy.types.Material.stf_active_material_property_index = bpy.props.IntProperty()
	bpy.types.Material.stf_material_property_value_refs = bpy.props.CollectionProperty(type=STF_Material_Value_Ref, name="STF Material Values")
	bpy.types.Material.stf_active_material_property_value_index = bpy.props.IntProperty()

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
	if hasattr(bpy.types.Material, "stf_active_material_property_value_index"):
		del bpy.types.Material.stf_active_material_property_value_index
