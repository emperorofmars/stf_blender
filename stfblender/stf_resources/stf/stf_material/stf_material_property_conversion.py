import bpy
import re

from .....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart
from .stf_material_definition import STF_Material_Value_Base
from .material_value_modules import blender_material_value_modules


def stf_material_export_blender_animation(context: STF_ExportContext, blender_resource: bpy.types.Object, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(len(blender_resource.material_slots) <= property_index or not blender_resource.material_slots[property_index].material):
		return None
	blender_material: bpy.types.Material = blender_resource.material_slots[property_index].material # pyright: ignore[reportAssignmentType]

	if(match := re.search(r"^(?P<property>stf_material_value_[a-zA-Z]+)\[(?P<index>[\d]+)\]", blender_property_path)):
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
				return STFPropertyPathPart([blender_resource.stf_info.stf_id, "instance", "material", property_index, material_property.property_type, value_index]) + mat_module.export_blender_animation(context, blender_property_path, property_value) # pyright: ignore[reportArgumentType, reportAttributeAccessIssue]
	return None


def stf_material_import_stf_animation_property_path_func(context: STF_ImportContext, stf_property_path: list[str], blender_resource: bpy.types.Object) -> BlenderPropertyPathPart | None:
	material_index = int(stf_property_path[1])
	material_property_type = stf_property_path[2]
	material_property_value_index = int(stf_property_path[3])
	blender_material = blender_resource.material_slots[int(stf_property_path[1])].material

	# let material_property
	for material_property in blender_material.stf_material.properties:
		if(material_property.property_type == material_property_type):
			break
	else:
		return None

	for mat_module in blender_material_value_modules:
		if(mat_module.property_name == material_property.value_property_name):
			return BlenderPropertyPathPart("MATERIAL", material_property.value_property_name + "[" + str(material_property_value_index) + "]", slot_link_property_index = material_index) + mat_module.import_stf_animation_property_path_func(context, stf_property_path[4:])
	return None

