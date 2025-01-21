import bpy


class StringProperty(bpy.types.PropertyGroup):
	value: bpy.props.StringProperty() # type: ignore


class STF_Material_Value_Base(bpy.types.PropertyGroup):
	value_id: bpy.props.IntProperty() # type: ignore


class STF_Material_Value_RawJson(STF_Material_Value_Base):
	json_text: bpy.props.StringProperty(name="Raw Json Text") # type: ignore
	# todo references to blender objects


class STF_Material_Value_Ref(bpy.types.PropertyGroup):
	value_property_name: bpy.props.StringProperty(name="Type") # type: ignore
	value_id: bpy.props.IntProperty() # type: ignore


class STF_Material_Property(bpy.types.PropertyGroup):
	stf_material_type: bpy.props.StringProperty(name="Type") # type: ignore
	multi_value: bpy.props.BoolProperty(name="Allows Multiple Values") # type: ignore
	values: bpy.props.CollectionProperty(type=STF_Material_Value_Ref, name="Value(s)") # type: ignore
	active_value_index: bpy.props.IntProperty() # type: ignore


class STF_Material_Definition(bpy.types.PropertyGroup):
	style_hints: bpy.props.CollectionProperty(type=StringProperty, name="Style Hints") # type: ignore
	# TODO shader targets


def register():
	bpy.types.Material.stf_is_source_of_truth = bpy.props.BoolProperty(name="STF Material Is Source Of Truth", default=False) # type: ignore

	bpy.types.Material.stf_material = bpy.props.PointerProperty(type=STF_Material_Definition, name="STF Material")
	bpy.types.Material.stf_material_properties = bpy.props.CollectionProperty(type=STF_Material_Property, name="STF Material Properties")
	bpy.types.Material.stf_active_material_property_index = bpy.props.IntProperty()
	bpy.types.Material.stf_material_property_values = bpy.props.CollectionProperty(type=STF_Material_Value_Ref, name="STF Material Values")

	bpy.types.Material.stf_material_value_raw_json = bpy.props.CollectionProperty(type=STF_Material_Value_RawJson, name="Raw Json Value")

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

	if hasattr(bpy.types.Material, "stf_material_value_raw_json"):
		del bpy.types.Material.stf_material_value_raw_json
