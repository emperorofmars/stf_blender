import bpy

"""
STF Components aren't natively supported by Blender, they are stored by the Blender-ID-thingy they belong to.
"""

class STF_Component_Ref(bpy.types.PropertyGroup): # Bringing polymorphism to Blender
	"""Defines the ID, by which the correct `STF_ComponentResourceBase` in the `blender_property_name` property of the appropriate Blender construct can be found"""
	stf_type: bpy.props.StringProperty(name="Type", options=set()) # type: ignore
	stf_id: bpy.props.StringProperty(name="ID", options=set()) # type: ignore
	blender_property_name: bpy.props.StringProperty(name="Blender Property Name", options=set()) # type: ignore

class InstanceModComponentRef(STF_Component_Ref):
	"""Used by armature instances to add or modify a component on an instance of a bone"""
	bone: bpy.props.StringProperty(name="Bone", options=set()) # type: ignore
	override: bpy.props.BoolProperty(name="Enable Instance Override", default=False, options=set()) # type: ignore


class STF_ComponentResourceBase(bpy.types.PropertyGroup):
	"""Base class for stf component property-groups"""
	stf_id: bpy.props.StringProperty(name="ID", description="Universally unique ID", options=set()) # type: ignore
	stf_name: bpy.props.StringProperty(name="STF Name", description="Optional component name", options=set()) # type: ignore
	exclusion_group: bpy.props.StringProperty(name="Exclusion Group", description="Game engines will import components of only one 'type' in this group.", options=set()) # type: ignore
	enabled: bpy.props.BoolProperty(name="Enabled", default=True, options={"ANIMATABLE"}) # type: ignore
