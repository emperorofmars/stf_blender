from typing import Callable


class STF_Module:
	"""Represents the functionality to process an STF type"""
	stf_type: str
	stf_kind: str

	priority: int = 0

	# Behaves like this type. For example a 'my.custom.super_fancy_mesh' can be like 'stf.mesh'.
	like_types: list[str] = []

	# List of application types this processor can export
	understood_application_types: list = []

	# (Import Context, Json Dict, ID, Optional Parent Application Object) -> The Application Object
	import_func: Callable[[any, dict, str, any], any]

	# (Export Context, Application Object, Optional Parent Application Object) -> (Json Dict, ID, Export Context)
	export_func: Callable[[any, any, any], tuple[dict, str, any]]

	# Get a list of application-components on the application object.
	# (Application Object) -> List[Application Component Object]
	get_components_func: Callable[[any], list[any]]


class STF_ExportHook(STF_Module):
	"""
		Provides a way to export an application-native 'thing' into STF, after a target processor has run.

		The 'understood_types' property from 'STF_Processor' can remain empty.

		For example, split normals are not defined as an explicit STF component in Blender, they are just a Blender native thing.
		The basic 'stf.mesh' STF resource doesn't support specifiying split normals.

		To do so, create a STF_ExportHook derived class with 'bpy.types.Mesh' as its 'target_application_types'.
		It's 'export_hook_func' checks if the model has split normals definitions, and creates a 'stf.mesh.split_normals' component on the underlying 'stf.mesh' resource.
	"""
	# List of application types this processor can hook into
	hook_target_application_types: list = []


class STF_ImportHook(STF_Module):
	"""
		Hook to import a resource based on custom logic.

		For example, in Blender, an object that has a mesh, must be created with the mesh data block at once.
		When a 'stf.node.spatial' contains a 'stf.instance.mesh' component, an 'STF_ImportHook' must target 'stf.node.spatial' and run its import logic, otherwise defer to the regular import logic.
	"""
	hook_target_stf_type: str
