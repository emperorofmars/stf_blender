import bpy
from typing import Any

from ..component import STF_Component_Ref
from ..resource_id import ensure_stf_id

"""
STF data-resources that aren't natively supported by Blender, similar to components, are stored by the Collection that represents the STF-Prefab.
"""

__all__ = ["STF_Data_Ref", "STF_DataResourceBase", "add_resource", "import_data_resource_base", "export_data_resource_base", "get_components_from_data_resource"]

class STF_Data_Ref(bpy.types.PropertyGroup):
	"""Defines the ID, by which the correct data-resource in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: bpy.props.StringProperty(name="Type", options=set()) # type: ignore
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name", options=set()) # type: ignore

class STF_DataResourceBase(bpy.types.PropertyGroup):
	"""Base class for stf data-resources which are non-native to Blender"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="Name", options=set()) # type: ignore
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components", options=set()) # type: ignore
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component", options=set()) # type: ignore


def add_resource(collection: bpy.types.Collection, blender_property_name: str, stf_id: str, stf_type: str) -> tuple[STF_Data_Ref, Any]:
	resource_ref: STF_Data_Ref = collection.stf_data_refs.add()
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


def import_data_resource_base(resource: STF_DataResourceBase, json_resource: Any):
	if("name" in json_resource): resource.stf_name = json_resource["name"]

def export_data_resource_base(stf_context: Any, stf_type: str, resource: STF_DataResourceBase) -> dict:
	ensure_stf_id(stf_context, resource, resource)
	ret = { "type": stf_type }
	if(resource.stf_name): ret["name"] = resource.stf_name
	return ret


def get_components_from_data_resource(resource: STF_DataResourceBase) -> list:
	collection = resource.id_data
	ret = []
	for component_ref in resource.stf_components:
		if(hasattr(collection, component_ref.blender_property_name)):
			components = getattr(collection, component_ref.blender_property_name)
			for component in components:
				if(component.stf_id == component_ref.stf_id):
					ret.append(component)
	return ret
