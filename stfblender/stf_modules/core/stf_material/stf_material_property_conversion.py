import bpy
import re
from typing import Callable

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from .stf_material_definition import STF_Material_Value_Base
from .material_value_modules import blender_material_value_modules


def _stf_material_resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: bpy.types.Object, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(len(application_object.material_slots) <= application_object_property_index or not application_object.material_slots[application_object_property_index].material):
		return None
	blender_material: bpy.types.Material = application_object.material_slots[application_object_property_index].material

	if(match := re.search(r"^(?P<property>stf_material_value_[a-zA-Z]+)\[(?P<index>[\d]+)\]", data_path)):
		if("property" not in match.groupdict() or "index" not in match.groupdict()):
			return None

		property_index = int(match.groupdict()["index"])
		property_type = match.groupdict()["property"]
		property_value_collection = getattr(blender_material, property_type)
		if(len(property_value_collection) <= property_index):
			return None
		property_value: STF_Material_Value_Base = getattr(blender_material, property_type)[int(match.groupdict()["index"])]

		# let material_property
		# let value_index
		for material_property in blender_material.stf_material.properties:
			if(material_property.value_property_name == property_type):
				for value_index, value_ref in enumerate(material_property.values):
					if(value_ref.value_id == property_value.value_id):
						break
				else:
					continue
				break
		else:
			return None

		for mat_module in blender_material_value_modules:
			if(mat_module.property_name == material_property.value_property_name):
				module_ret = mat_module.resolve_property_path_to_stf_func(context, data_path, property_value)
				if(module_ret):
					value_path, conversion_func, index_table = module_ret # Ignore Target Object for now
					return [application_object.stf_info.stf_id, "instance", "material", application_object_property_index, material_property.property_type, value_index] + value_path, conversion_func, index_table
	return None


def _stf_material_resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: bpy.types.Object) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	material_index = int(stf_path[1])
	material_property_type = stf_path[2]
	material_property_value_index = int(stf_path[3])
	blender_material = application_object.material_slots[int(stf_path[1])].material

	# let material_property
	for material_property in blender_material.stf_material.properties:
		if(material_property.property_type == material_property_type):
			break
	else:
		return None

	for mat_module in blender_material_value_modules:
		if(mat_module.property_name == material_property.value_property_name):
			module_ret = mat_module.resolve_stf_property_to_blender_func(context, stf_path[4:])
			if(module_ret):
				value_path, index_table, conversion_func = module_ret # Ignore Target Object for now
				return None, material_index, "MATERIAL", material_property.value_property_name + "[" + str(material_property_value_index) + "]" + value_path, index_table, conversion_func
	return None

