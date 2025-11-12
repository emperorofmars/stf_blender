import bpy
from typing import Callable

from .stf_module import STF_Module
from ..base.blender_grr.blender_grr import BlenderGRR
from ..utils.armature_bone import ArmatureBone

"""
Components aren't natively supported by Blender, they are stored by the Blender-ID-thingy they belong to.
"""

class STF_Component_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct component in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: bpy.props.StringProperty(name="Type", options=set()) # type: ignore
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name", options=set()) # type: ignore


class STF_BlenderComponentBase(bpy.types.PropertyGroup):
	"""Base class for stf component property-groups"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional component name", options=set()) # type: ignore
	overrides: bpy.props.CollectionProperty(type=BlenderGRR, name="Overrides", description="If this component is parsed by a game-engine, these components should be ignored", options=set()) # type: ignore
	enabled: bpy.props.BoolProperty(name="Enabled", default=True, options={"ANIMATABLE"}) # type: ignore


class STF_BlenderComponentModule(STF_Module):
	"""Extension to STF_Module which also associates a function to draw the component in Blender's UI"""
	blender_property_name: str
	filter: list
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentBase) -> None
	draw_component_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, any, any], None]


class STF_Component_Editmode_Resistant_Reference:
	def __init__(self, component: STF_BlenderComponentBase, context_object: any):
		self.component_id = component.stf_id
		self.stf_id = component.stf_id
		if(type(context_object) == bpy.types.Bone):
			self.armature_bone = ArmatureBone(component.id_data, context_object.name)
		else:
			self.component = component
	def get(self) -> STF_BlenderComponentBase:
		if(hasattr(self, "component")):
			return self.component
		else:
			for component_ref in self.armature_bone.get_bone().stf_info.stf_components:
				if(component_ref.stf_id == self.component_id):
					for component in getattr(self.armature_bone.get_bone(), component_ref.blender_property_name):
						if(component.stf_id == self.component_id):
							return component
		return None


class InstanceModComponentRef(STF_Component_Ref):
	"""Used by armature instances to add or modify a component on an instance of a bone"""
	bone: bpy.props.StringProperty(name="Bone") # type: ignore
	override: bpy.props.BoolProperty(name="Enable Instance Override", default=False) # type: ignore

class STF_BlenderBoneComponentModule(STF_BlenderComponentModule):
	"""Use for components that are allowed on bones and are animatable or can have different values per instance of the armature"""
	# (layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentBase) -> None
	draw_component_instance_func: Callable[[bpy.types.UILayout, bpy.types.Context, STF_Component_Ref, any, any], None]
	# (context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_BlenderComponentBase, standin_component: STF_BlenderComponentBase) -> None
	set_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, any, any, any], None]

	# (context: bpy.types.Context, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentBase, context_object: any) -> json_resource: dict
	serialize_component_instance_standin_func: Callable[[bpy.types.Context, STF_Component_Ref, STF_BlenderComponentBase, any], dict]
	# (context: bpy.types.Context, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STF_BlenderComponentBase, context_object: any) -> None
	parse_component_instance_standin_func: Callable[[bpy.types.Context, dict, STF_Component_Ref, STF_BlenderComponentBase, any], None]



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

