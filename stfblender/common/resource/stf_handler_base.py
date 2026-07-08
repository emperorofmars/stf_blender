from typing import Any, Protocol
from collections.abc import Callable

from .. import STF_ImportContext, STF_ExportContext, BlenderPropertyPathPart, STFPropertyPathPart, STFReport


class STF_HandlerBase(Protocol):
	"""
	Represents functionality to import and export an STF resource
	"""

	stf_type: str
	"""STF type identifier"""

	stf_category: str
	"""The STF category string must match the `STF_Category` enum. This property is useful for validation"""

	understood_application_types: list
	"""List of application types this module can export"""

	priority: int = 0
	"""If a module for the same `stf_type` is registered, the priority will decide which is preferred"""

	like_types: list[str] = []
	"""Behaves like this types. For example a `my.custom.super_fancy_mesh` is like `mesh`"""

	can_handle_application_object_func: Callable[[Any], int]
	"""
	`def can_handle_application_object_func(blender_object: Any) -> int`

	Return a priority for handling this application type. If the priority is negative, don't use this module even if no other is found

	:param Any blender_object: Object to check
	:return int: The determined priority value
	"""

	import_func: Callable[[STF_ImportContext, dict, str, Any | None], Any | STFReport]
	"""
	`def import_func(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any | None) -> Any | STFReport`

	Import the STF Resource into a Blender resource

	:param STF_ImportContext context: Context where further resources can be imported, buffers can be retrieved, callbacks & cleanup-callbacks can be registered
	:param dict json_resource: STF JSON resource
	:param str stf_id: The unique ID of the resource
	:param Any | None context_object: Optional context Blender object within which the blender_object exists. e.g. the Collection for an Object, or Armature for a Bone
	:return Any: The imported Blender object
	:return STFReport: In case of failure
	"""

	export_func: Callable[[STF_ExportContext, Any, Any | None], tuple[dict, str] | STFReport]
	"""
	`def export_func(context: STF_ExportContext, blender_object: Any, context_object: Any | None) -> tuple[dict, str] | STFReport`

	Export the Blender resource into an STF resource

	:param STF_ExportContext context: Context where further resources can be exported, buffers, callbacks & cleanup-callbacks can be registered
	:param Any blender_object: Blender object to be exported
	:param Any | None context_object: Optional context Blender object within which the blender_object exists. e.g. the Collection for an Object, or Armature for a Bone
	:return tuple[dict, str]: A Tuple of the exported JSON resource and the stf_id
	:return STFReport: In case of failure
	"""


	### Properties for animation handling

	understood_application_property_path_types: list[Any] = []
	"""List of application types from which this module can convert paths"""

	understood_application_property_path_parts: list[str] = []
	"""List of paths which this component can convert into stf paths"""

	resolve_property_path_to_stf_func: Callable[[STF_ExportContext, Any, int, str], STFPropertyPathPart | None]
	"""
	`def resolve_property_path_to_stf_func(context: STF_ExportContext, blender_object: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None`
	Resolves a Blender animation property path part into STF

	:param STF_ExportContext context: Get subsequent property-path parts from referenced Blender resources
	:param Any blender_object: Blender object for which the property path has to be resolved
	:param int property_index: E.g. index of a vector component
	:param str blender_property_path: Blender animation property path
	:return STFPropertyPathPart: Success
	:return None: Failure
	"""

	resolve_stf_property_to_blender_func: Callable[[STF_ImportContext, list[str], Any], BlenderPropertyPathPart | None]
	"""
	`def resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_property_path: list[str], blender_object: Any) -> BlenderPropertyPathPart | None`

	Resolves an STF animation property path part into Blender

	:param STF_ImportContext context: Get subsequent property-path parts from referenced STF resources
	:param list[str], stf_property_path: STF animation property path
	:param Any blender_object: Blender object for which the property path has to be resolved
	:return BlenderPropertyPathPart: Success
	:return None: Failure
	"""


	### Handling components if applicable. `get_components_func` must be assigned/implemented if the resource supports components

	get_components_func: Callable[[Any], list[Any] | None]
	"""
	`def get_components_func(blender_object: Any) -> list[Any] | None`

	Get a list of application-components on the application object.

	:param Any blender_object: Blender object to retrieve its components from
	:return list[Any]: Blender stf component objects
	:return None: No components present
	"""

	get_components_holder_func: Callable[[Any], Any | None]
	"""
	`def get_components_holder_func(blender_object: Any) -> Any | None`

	Get the object which has the `stf_components` property. Mostly a workaround for Bone references getting invalidated by Blender on mode-switch.

	:param Any blender_object: Blender object for which to get the component-holder property
	:return Any: Blender object with the component-holder property
	:return None: No components present
	"""
