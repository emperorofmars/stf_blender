import bpy
from enum import Enum
from typing import Callable

from .property_path_part import BlenderPropertyPathPart, STFPropertyPathPart


class STF_Kind(Enum):
	DATA = 0
	NODE = 1
	INSTANCE = 2
	COMPONENT = 3


class STF_Module:
	"""Represents functionality to import and export an STF resource"""
	stf_type: str

	# The STF kind string must match the STF_Kind enum. This property is useful for validation.
	stf_kind: str

	# If a module for the same stf_type is registered, the priority will decide which is preferred.
	priority: int = 0

	# Behaves like this types. For example a 'my.custom.super_fancy_mesh' is like 'mesh'.
	like_types: list[str] = []

	# List of application types this module can export
	understood_application_types: list = []

	# Return a priority for handling this application type. If the priority is negative, don't use this module even if no other is found.
	can_handle_application_object_func: Callable[[any], int]


	# (Import Context, Json Dict, ID, Optional Parent Application Object) -> The Application Object
	import_func: Callable[[any, dict, str, any], any]

	# (Export Context, Application Object, Optional Parent Application Object) -> (Json Dict, ID)
	export_func: Callable[[any, any, any], tuple[dict, str]]

	"""
	Properties for animation handling
	"""
	# List of application types from which this module can convert paths.
	understood_application_property_path_types: list[any] = []

	# List of paths which this component can convert into stf paths.
	understood_application_property_path_parts: list[str] = []

	# (Export Context, Application Object, Application Object Property Index,, Application Path) -> BlenderPropertyPathPart
	resolve_property_path_to_stf_func: Callable[[any, any, int, str], STFPropertyPathPart]

	# (Import Context, Target Application Node, List of STF Path Elements, Base Target Application Object) -> BlenderPropertyPathPart
	resolve_stf_property_to_blender_func: Callable[[any, list[str], any], BlenderPropertyPathPart]

	"""
	Handling components if applicable. `get_components_func` must be assigned if the resource supports components
	"""
	# Get a list of application-components on the application object.
	# (Application Object) -> List[Application Component Object]
	get_components_func: Callable[[any], list[any]]

	# Get the object which has the `stf_components` property. Mostly a workaround for Bone references getting invalidated by Blender on mode-switch.
	get_components_holder_func: Callable[[any], any]
