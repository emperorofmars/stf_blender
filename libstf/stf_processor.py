from typing import Callable


class STF_Processor:
	""" Represents the functionality of a module to process an STF type. """
	stf_type: str
	stf_kind: str

	# List of application types this processor can export
	understood_types: list = []

	# (Import Context, Json Dict, ID) -> The Application Object
	import_func: Callable[[any, dict, str], any]

	# (Export Context, The Application Object) -> (Json Dict, ID)
	export_func: Callable[[any, any], tuple[dict, str]]

	# Behaves like this type. For example a 'my.custom.super_fancy_mesh' can be like 'stf.mesh'.
	like_stf_type: str | None


class STF_ExportHook(STF_Processor):
	"""
		Provides a way to export an application-native 'thing' into STF, after a target processor has run.

		The 'understood_types' property from 'STF_Processor' can remain empty.

		For example, split normals are not defined as an explicit STF component in Blender, they are just a Blender native thing.
		The basic 'stf.mesh' STF resource doesn't support specifiying split normals.

		To do so, create a STF_ExportHook derived class with 'stf.mesh' as its 'target_stf_type'.
		It's 'export_func' checks if the model has split normals definitions, and creates a 'stf.mesh.split_normals' component on the underlying 'stf.mesh'.
	"""
	target_stf_types: list[str]

	# (Export Context, The Application Object) -> (Json Dict, ID)
	export_hook_func: Callable[[any, any], tuple[dict, str]]
