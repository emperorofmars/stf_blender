import bpy
from enum import Enum
from typing import Callable


class STF_Kind(Enum):
	DATA = 0
	NODE = 1
	INSTANCE = 2
	COMPONENT = 3


class STF_Module:
	"""Represents the functionality to import and export an STF resource"""
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
	Properties for animation handling.
	"""
	# List of application types from which this module can convert paths.
	understood_application_property_path_types: list[any] = []

	# List of paths which this component can convert into stf paths.
	understood_application_property_path_parts: list[str] = []

	# (Export Context, Application Object, Application Object Property Index,, Application Path) -> (List of STF Path Elements, Function to Application translate animation keys to STF, Track index conversion table)
	resolve_property_path_to_stf_func: Callable[[any, any, int, str], tuple[list[str], Callable[[int, any], any], list[int]]]

	# (Import Context, Target Application Node, List of STF Path Elements, Base Target Application Object) -> (Application Object, Application Object Property Index, Property Type, Application Path, Property Index, Function to translate STF animation keys to the Application)
	resolve_stf_property_to_blender_func: Callable[[any, list[str], any], tuple[any, int, any, any, list[int], Callable[[int, any], any]]]

	"""
	If a resource can have components, these functions must be implemented.
	"""
	# Get a list of application-components on the application object.
	# (Application Object) -> List[Application Component Object]
	get_components_func: Callable[[any], list[any]]

	# Add the object to add aa component to
	get_components_holder_func: Callable[[any], any]


class STF_ExportComponentHook:
	"""Provides a way to export an application-native 'thing' into STF, after a target module has run.

	The 'understood_types' property from 'STF_Module' can remain empty.

	For example, split normals are not defined as an explicit STF component in Blender, they are just a Blender native thing.
	The basic 'stf.mesh' STF resource doesn't support specifiying split normals.

	To do so, create a STF_ExportComponentHook derived class with 'bpy.types.Mesh' as its 'hook_target_application_types'.
	The 'hook_can_handle_application_object_func' checks if the model has split normals definitions, and the 'hook_apply_func' creates a 'stf.mesh.split_normals' component on the Mesh resource"""
	hook_name: str

	# List of application types this module can hook into
	hook_target_application_types: list = []

	hook_can_handle_application_object_func: Callable[[any], bool]

	# (Export Context, Application Object, Optional Parent Application Object)
	hook_apply_func: Callable[[any, any, any], None]


class STF_Component_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct component in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name") # type: ignore

class STF_Info(bpy.types.PropertyGroup):
	"""Basic STF properties"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional Name for STF export") # type: ignore
	stf_name_source_of_truth: bpy.props.BoolProperty(name="STF Name Is Source Of Truth", description="Use Blender name or specify one manually") # type: ignore
	stf_components: bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	stf_active_component_index: bpy.props.IntProperty(name="Selected Component") # type: ignore


class STF_BlenderComponentModule(STF_Module):
	"""Extension to STF_Module which also associates a function to draw the component in Blender's UI"""
	blender_property_name: str
	filter: list
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentModule) -> None
	draw_component_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, any, any], None]


class InstanceModComponentRef(STF_Component_Ref):
	"""Used by armature instances to add or modify a component on an instance of a bone"""
	bone: bpy.props.StringProperty(name="Bone") # type: ignore
	override: bpy.props.BoolProperty(name="Enable Instance Override", default=False) # type: ignore

class STF_BlenderBoneComponentModule(STF_BlenderComponentModule):
	"""Use for components that are allowed on bones and are animatable or can have different values per instance of the armature"""
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentModule) -> None
	draw_component_instance_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, any, any], None]
	# (context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentModule, standin_component: STF_BlenderComponentModule) -> None
	set_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, any, any, any], None]

	# (context: bpy.types.Context, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentModule, context_object: any) -> json_resource: dict
	serialize_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, STF_BlenderComponentModule, any], dict]
	# (context: bpy.types.Context, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentModule, context_object: any) -> None
	parse_component_instance_standin_func: Callable[[bpy.types.Context, dict, STF_Component_Ref, STF_BlenderComponentModule, any], None]


class STF_BlenderComponentOverride(bpy.types.PropertyGroup):
	"""If this component is parsed by a game-engine, the target component should be ignored"""
	target_id: bpy.props.StringProperty(name="Target ID") # type: ignore

class STF_BlenderComponentBase(bpy.types.PropertyGroup):
	"""Base class for stf component property-groups"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID") # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional component name") # type: ignore
	overrides: bpy.props.CollectionProperty(type=STF_BlenderComponentOverride, name="Overrides", description="If this component is parsed by a game-engine, these components should be ignored") # type: ignore
	enabled: bpy.props.BoolProperty(name="Enabled", default=True) # type: ignore
