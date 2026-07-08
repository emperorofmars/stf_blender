import bpy
from typing import Any
from collections.abc import Callable

from ..protocols import PSTF_ExportContext, PSTF_ImportContext, PSTF_Component_Ref, PSTF_ComponentResourceBase
from .armature_bone import ArmatureBone
from .id_utils import ensure_stf_id


def add_component(context_object: Any, blender_property_name: str, stf_id: str, stf_type: str, components_ref_property: Any = None, name = None) -> tuple[PSTF_Component_Ref, PSTF_ComponentResourceBase]:
	if(components_ref_property is None):
		if(hasattr(context_object, "stf_components")):
			components_ref_property = context_object.stf_components
			context_object = context_object.id_data
		else:
			components_ref_property = context_object.stf_info.stf_components
	component_ref: PSTF_Component_Ref = components_ref_property.add()
	component_ref.name = stf_id
	component_ref.stf_id = stf_id
	component_ref.stf_type = stf_type
	component_ref.blender_property_name = blender_property_name

	new_component = getattr(context_object, blender_property_name).add()
	new_component.name = stf_id
	new_component.stf_id = component_ref.stf_id
	if(name):
		new_component.stf_name = name.replace("$parent", context_object.name)

	if(blender_property_name == "stf_json_fallback_component"):
		new_component.json = "{\"type\": \"" + stf_type + "\"}"

	return (component_ref, new_component)


class STF_Component_Editmode_Resistant_Reference:
	"""Because Blender"""
	def __init__(self, component: PSTF_ComponentResourceBase, context_object: Any):
		self.component_id = component.stf_id
		self.stf_id = component.stf_id
		if(type(context_object) is bpy.types.Bone):
			self.armature_bone = ArmatureBone(component.id_data, context_object.name) # pyright: ignore[reportArgumentType]
		else:
			self.component = component

	def get(self) -> PSTF_ComponentResourceBase:
		if(hasattr(self, "component")):
			return self.component
		else:
			for component_ref in self.armature_bone.get_bone().stf_info.stf_components:
				if(component_ref.stf_id == self.component_id):
					for component in getattr(self.armature_bone.get_bone(), component_ref.blender_property_name):
						if(component.stf_id == self.component_id):
							return component
		raise Exception("Invalid code path")


def preserve_component_reference(component: PSTF_ComponentResourceBase, blender_property_name: str, context_object: Any) -> Callable[[], PSTF_ComponentResourceBase]:
	component_id = component.stf_id
	if(type(context_object) is bpy.types.Bone and type(component.id_data) is bpy.types.Armature):
		armature_bone = ArmatureBone(component.id_data, context_object.name)
		def _get_component() -> PSTF_ComponentResourceBase:
			for candidate in getattr(armature_bone.get_bone(), blender_property_name):
				if(candidate.stf_id == component_id):
					return candidate
			raise Exception("Invalid code path")
	elif(type(context_object) is ArmatureBone):
		def _get_component() -> PSTF_ComponentResourceBase:
			for candidate in getattr(context_object.get_bone(), blender_property_name):
				if(candidate.stf_id == component_id):
					return candidate
			raise Exception("Invalid code path")
	else:
		def _get_component() -> PSTF_ComponentResourceBase:
			for candidate in getattr(context_object, blender_property_name):
				if(candidate.stf_id == component_id):
					return candidate
			raise Exception("Invalid code path")
	return _get_component


def get_components_from_object(blender_object: Any) -> list[Any]:
	"""Retrieves Blender STF components from an Blender object"""
	ret = []
	if(hasattr(blender_object, "stf_info")):
		for component_ref in blender_object.stf_info.stf_components:
			if(hasattr(blender_object, component_ref.blender_property_name)):
				components = getattr(blender_object, component_ref.blender_property_name)
				for component in components:
					if(component.stf_id == component_ref.stf_id):
						ret.append(component)
	return ret


def import_component_base(context: PSTF_ImportContext, component: PSTF_ComponentResourceBase, json_resource: dict, blender_property_name: str, context_object: Any):
	if("name" in json_resource): component.stf_name = json_resource["name"]
	if("exclusion_group" in json_resource and json_resource["exclusion_group"]):
		component.exclusion_group = json_resource["exclusion_group"]
		if(component.exclusion_group not in context._root_collection.stf_exclusion_groups):
			new_g = context._root_collection.stf_exclusion_groups.add()
			new_g.name = component.exclusion_group
			new_g.group_name = component.exclusion_group
	if("enabled" in json_resource):
		component.enabled = json_resource["enabled"]

def export_component_base(context: PSTF_ExportContext, stf_type: str, component: PSTF_ComponentResourceBase, blender_property_name: str, context_object: Any) -> dict:
	ensure_stf_id(context, component, component)
	ret: dict[str, Any] = { "type": stf_type }
	if(component.stf_name): ret["name"] = component.stf_name
	if(component.exclusion_group): ret["exclusion_group"] = component.exclusion_group
	if(not component.enabled): ret["enabled"] = False
	return ret
