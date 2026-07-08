import bpy
from typing import Any

from ..protocols import PSTF_Data_Ref, PSTF_DataResourceBase
from .id_utils import ensure_stf_id


def add_resource(collection: bpy.types.Collection, blender_property_name: str, stf_id: str, stf_type: str) -> tuple[PSTF_Data_Ref, Any]:
	resource_ref: PSTF_Data_Ref = collection.stf_data_refs.add()
	resource_ref.stf_id = stf_id
	resource_ref.stf_type = stf_type
	resource_ref.blender_property_name = blender_property_name
	resource_ref.name = stf_id

	new_resource = getattr(collection, blender_property_name).add()
	new_resource.stf_id = stf_id
	new_resource.name = stf_id

	if(blender_property_name == "stf_json_fallback_data"):
		new_resource.json = "{\"type\": \"" + stf_type + "\"}"

	return (resource_ref, new_resource)


def get_components_from_data_resource(resource: PSTF_DataResourceBase) -> list:
	collection = resource.id_data
	ret = []
	for component_ref in resource.stf_components:
		if(hasattr(collection, component_ref.blender_property_name)):
			components = getattr(collection, component_ref.blender_property_name)
			for component in components:
				if(component.stf_id == component_ref.stf_id):
					ret.append(component)
	return ret


def import_data_resource_base(resource: PSTF_DataResourceBase, json_resource: Any):
	if("name" in json_resource): resource.stf_name = json_resource["name"]

def export_data_resource_base(stf_context: Any, stf_type: str, resource: PSTF_DataResourceBase) -> dict:
	ensure_stf_id(stf_context, resource, resource)
	ret = { "type": stf_type }
	if(resource.stf_name): ret["name"] = resource.stf_name
	return ret
