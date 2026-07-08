import bpy
from typing import Any, Callable, Protocol

from ..stf_handler_base import STF_HandlerBase
from ... import STF_Category, STF_ImportContext, STF_ExportContext

"""
STF Components aren't natively supported by Blender, they are stored by the Blender-ID-thingy they belong to.
"""

class PSTF_Component_Ref(Protocol): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct `STF_ComponentResourceBase` in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: str
	stf_id: str
	blender_property_name: str

class STF_Component_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct `STF_ComponentResourceBase` in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: bpy.props.StringProperty(name="Type", options=set()) # type: ignore
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name", options=set()) # type: ignore

class PInstanceModComponentRef(PSTF_Component_Ref, Protocol):
	"""Used by armature instances to add or modify a component on an instance of a bone"""
	bone: str
	override: bool

class InstanceModComponentRef(STF_Component_Ref):
	"""Used by armature instances to add or modify a component on an instance of a bone"""
	bone: bpy.props.StringProperty(name="Bone", options=set()) # type: ignore
	override: bpy.props.BoolProperty(name="Enable Instance Override", default=False, options=set()) # type: ignore


class PSTF_ComponentResourceBase(Protocol):
	"""Base class for stf component property-groups"""
	stf_id: str
	stf_name: str
	exclusion_group: str
	enabled: bool

class STF_ComponentResourceBase(bpy.types.PropertyGroup):
	"""Base class for stf component property-groups"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional component name", options=set()) # type: ignore
	exclusion_group: bpy.props.StringProperty(name="Exclusion Group", description="Game engines will import components of only one 'type' in this group.", options=set()) # type: ignore
	enabled: bpy.props.BoolProperty(name="Enabled", default=True, options={"ANIMATABLE"}) # type: ignore


class STF_Handler_Component(STF_HandlerBase, Protocol):
	"""Extension to STF_Module which also associates a function to draw the component in Blender's UI"""

	stf_category = STF_Category.COMPONENT

	blender_property_name: str
	"""getattr(blender_ID_thingy, blender_property_name) has to return a list of components of this modules type on the respective blender_ID_thingy"""

	filter: list
	"""Filter of types this component can be placed on."""

	draw_component_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, Any, Any], None]
	"""
	`def draw_component_func(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_ComponentResourceBase) -> None`

	Draw the components GUI

	:param bpy.types.UILayout layout:
	:param bpy.types.Context context:
	:param STF_Component_Ref component_ref:
	:param Any context_object: The blender construct this component exists on
	:param STF_ComponentResourceBase component: STF Component for which to draw GUI for
	"""

	process_func: Callable[[STF_ComponentResourceBase, Any, Any], None]
	"""
	`def process_func(component: STF_ComponentResourceBase, context_object: Any, apply_object: Any) -> None`

	If the component can setup Blender native constructs, e.g. IK constraints on a PoseBone, implement this func.
	The apply_object should be the final instance where the component functionality should be applied to.
	In the case of an IK constraint on a bone, the context_object will be bpy.types.Bone, and the apply object will be the bpy.types.Object that instantiates the Armature with the Bone.
	This way the IK constraint will be applied to every Armature instance.

	:param STF_ComponentResourceBase component: STF Component
	:param Any context_object: The blender construct this component exists on
	:param Any apply_object: Object for the component to apply its functionality to
	"""

	pretty_name_template: str
	"""
	Default stf_name newly added components will get.
	Substitutes $parent with the name of the object the component is added to.
	"""


class STF_Handler_BoneComponent(STF_Handler_Component, Protocol):
	"""Use for components that are allowed on bones and are animatable or can have different values per instance of the armature"""

	draw_component_instance_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, Any, STF_ComponentResourceBase], None]
	"""
	`def draw_component_instance_func(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_ComponentResourceBase) -> None`

	Draw the component-instances GUI

	:param bpy.types.UILayout layout:
	:param bpy.types.Context context:
	:param STF_Component_Ref component_ref:
	:param Any context_object: The blender construct this component exists on
	:param STF_ComponentResourceBase component: STF component for which to draw GUI for
	"""

	set_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, Any, Any, Any], None]
	"""
	`def set_component_instance_standin_func(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_ComponentResourceBase, standin_component: STF_ComponentResourceBase) -> None`

	Apply the components values to an instance standin (on an Armature instance).

	:param STF_Component_Ref component_ref:
	:param bpy.types.Context context:
	:param Any context_object: The blender construct this component exists on
	:param STF_ComponentResourceBase component: Source STF component
	:param STF_ComponentResourceBase standin_component: Target STF component instance
	"""

	serialize_component_instance_standin_func: Callable[[STF_ExportContext, STF_Component_Ref, STF_ComponentResourceBase, Any], dict]
	"""
	`def (context: bpy.types.Context, component_ref: STF_Component_Ref, standin_component: STF_ComponentResourceBase, context_object: Any) -> dict`
	"""

	parse_component_instance_standin_func: Callable[[STF_ImportContext, dict, STF_Component_Ref, STF_ComponentResourceBase, Any], None]
	"""
	`def parse_component_instance_standin_func(context: bpy.types.Context, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STF_ComponentResourceBase, context_object: Any) -> None`
	"""


class STF_ExportComponentHook(Protocol):
	"""
	Mixin class to be inherited by an `STF_HandlerBase` derivative.
	Provides a way to export Blender things into STF, after an STF handler has run.

	The `understood_types` property from `STF_Handler` can remain empty.

	For example, split normals are not defined as an explicit STF component in Blender, they are just a Blender native thing.
	The basic 'stf.mesh' STF resource doesn't support specifying split normals.

	To do so, create a STF_ExportComponentHook derived class with 'bpy.types.Mesh' as its 'hook_target_application_types'.
	The 'hook_can_handle_application_object_func' checks if the model has split normals definitions, and the 'hook_apply_func' creates a 'stf.mesh.split_normals' component on the Mesh resource.
	"""

	hook_name: str

	hook_target_application_types: list = []
	"""List of application types this module can hook into"""

	hook_can_handle_application_object_func: Callable[[Any], bool]
	"""
	`def hook_can_handle_application_object_func(blender_object: Any) -> bool`
	"""

	hook_apply_func: Callable[[STF_ExportContext, Any, Any], None]
	"""
	`def hook_apply_func(context: STF_ExportContext, blender_object: Any, context_object: Any) -> None`
	"""
