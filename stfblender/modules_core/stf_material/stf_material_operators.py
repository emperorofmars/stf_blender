import bpy

from .stf_material_definition import STF_Material_Property, STF_Material_Value_Module_Base, STF_Material_Value_Ref
from .material_value_modules import blender_material_value_modules


def add_property(blender_material: bpy.types.Material, property_type: str, value_module: STF_Material_Value_Module_Base, group: str = None) -> tuple[STF_Material_Property, STF_Material_Value_Ref, STF_Material_Value_Module_Base]:
	prop = blender_material.stf_material_properties.add()
	prop.property_type = property_type
	prop.value_property_name = value_module.property_name
	prop.value_type = value_module.value_type
	if(group): prop.group = group

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


class STFAddMaterialProperty(bpy.types.Operator):
	bl_idname = "stf.add_material_property"
	bl_label = "Add Property"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	property_type: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		for mat_module in blender_material_value_modules:
			if(mat_module.value_type == context.scene.stf_material_value_modules):
				add_property(context.material, self.property_type, mat_module)
				return {"FINISHED"}
		self.report({'ERROR'}, "Invalid material value module!")
		return {"CANCELLED"}

class STFRemoveMaterialProperty(bpy.types.Operator):
	bl_idname = "stf.remove_material_property"
	bl_label = "Remove"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		remove_property(context.material, self.index)
		return {"FINISHED"}


class STFAddMaterialPropertyValue(bpy.types.Operator):
	bl_idname = "stf.add_material_property_value"
	bl_label = "Add Value"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		add_value_to_property(context.material, self.index)
		return {"FINISHED"}

class STFRemoveMaterialPropertyValue(bpy.types.Operator):
	bl_idname = "stf.remove_material_property_value"
	bl_label = "Remove"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		remove_property_value(context.material, self.index)
		return {"FINISHED"}
