from enum import Enum
from typing import Callable


class STF_Kind(Enum):
	DATA = 0
	NODE = 1
	INSTANCE = 2
	COMPONENT = 3


class STF_Module:
	"""
	Represents the functionality to import and export an STF resource.
	"""
	stf_type: str

	# The STF kind string must match the STF_Kind enum. This property is useful for validation.
	stf_kind: str

	# If a module for the same target stf or application type is registered, the priority will decide which is preferred.
	priority: int = 0

	# Behaves like this types. For example a 'my.custom.super_fancy_mesh' is like 'mesh'.
	like_types: list[str] = []

	# List of application types this module can export
	understood_application_types: list = []

	# Return a priority for handling this application type. If the priority is negative, don't use this module.
	can_handle_application_object_func: Callable[[any], int]


	# (Import Context, Json Dict, ID, Optional Parent Application Object) -> The Application Object
	import_func: Callable[[any, dict, str, any], any]

	# (Export Context, Application Object, Optional Parent Application Object) -> (Json Dict, ID)
	export_func: Callable[[any, any, any], tuple[dict, str]]


	understood_application_property_path_types: list[any] = []
	understood_application_property_path_parts: list[str] = []

	# (Export Context, Application Object, Application Path, Property Index) -> (List of STF Path Elements, Function to Application translate animation keys to STF)
	resolve_property_path_to_stf_func: Callable[[any, any, str, int], tuple[list[str], Callable[[any], any]]]

	# (Import Context, Target Application Node, List of STF Path Elements) -> (Application Object, Property Type, Application Path, Property Index, Function to translate STF animation keys to the Application)
	resolve_stf_property_to_blender_func: Callable[[any, list[str]], tuple[any, any, any, int, Callable[[any], any]]]


	# Get a list of application-components on the application object.
	# (Application Object) -> List[Application Component Object]
	get_components_func: Callable[[any], list[any]]


class STF_ExportComponentHook(STF_Module):
	"""
	Provides a way to export an application-native 'thing' into STF, after a target module has run.

	The 'understood_types' property from 'STF_Module' can remain empty.

	For example, split normals are not defined as an explicit STF component in Blender, they are just a Blender native thing.
	The basic 'stf.mesh' STF resource doesn't support specifiying split normals.

	To do so, create a STF_ExportHook derived class with 'bpy.types.Mesh' as its 'target_application_types'.
	It's 'export_hook_func' checks if the model has split normals definitions, and creates a 'stf.mesh.split_normals' component on the underlying 'stf.mesh' resource.
	"""
	# List of application types this module can hook into
	hook_target_application_types: list = []

	hook_can_handle_application_object_func: Callable[[any], tuple[bool, list[any]]]
