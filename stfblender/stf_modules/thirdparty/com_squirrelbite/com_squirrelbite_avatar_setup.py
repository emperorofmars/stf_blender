import bpy
from typing import Any

from ....common import STF_ExportContext, STF_ImportContext, STFReportSeverity, STFReport
from ....common.module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....common.helpers import import_resource, register_exported_resource, draw_list, poll_valid_animations
from ....common.blender_grr import *

from ....common.module_component.component_utils import add_component, export_component_base, import_component_base


_stf_type = "com.squirrelbite.avatar_setup"
_blender_property_name = "com_squirrelbite_avatar_setup"


class Toggle(bpy.types.PropertyGroup):
	animation_on: bpy.props.PointerProperty(name="On", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore
	animation_off: bpy.props.PointerProperty(name="Off", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore

class PersistentPuppet(bpy.types.PropertyGroup):
	type: bpy.props.EnumProperty(name="Type", items=(("1d", "1D", ""), ("2d", "2D", ""))) # type: ignore
	property_enabled: bpy.props.StringProperty(name="Enabled Property", options=set()) # type: ignore
	property_x: bpy.props.StringProperty(name="Value Property", options=set()) # type: ignore
	property_y: bpy.props.StringProperty(name="Value Property", options=set()) # type: ignore
	blendtree: bpy.props.PointerProperty(type=STFDataResourceReference, options=set()) # type: ignore


class Squirrelbite_Avatar_Setup(STF_BlenderComponentBase):
	toggles_pre: bpy.props.CollectionProperty(name="Overridable Toggles", type=Toggle, options=set()) # type: ignore
	puppets_pre: bpy.props.CollectionProperty(name="Persistent Puppets", type=PersistentPuppet, options=set()) # type: ignore

	puppets: bpy.props.CollectionProperty(name="Puppets", type=STFDataResourceReference, options=set()) # type: ignore
	toggles: bpy.props.CollectionProperty(name="Toggles", type=Toggle, options=set()) # type: ignore

	breathing_normal: bpy.props.PointerProperty(name="Breathing Normal Animation", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore
	breathing_intense: bpy.props.PointerProperty(name="Breathing Intense Animation", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore

	additive_excited: bpy.props.PointerProperty(name="Additive Excited Animation", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore
	additive_idle: bpy.props.PointerProperty(name="Additive Idle Animation", type=bpy.types.Action, options=set(), poll=poll_valid_animations) # type: ignore


def _draw_func_toggle(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box_inner = layout.box()
	row = box_inner.row(align=True)
	col = row.column(align=True)
	col.prop(element, "name")
	col.prop(element, "animation_on")
	col.prop(element, "animation_off")
	return row

def _draw_func_puppet(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box = layout.box()
	row = box.row(align=True)
	col = row.column(align=True)
	col.prop(element, "type")
	col.prop(element, "name")
	col.label(text="Properties")
	col.prop(element, "property_enabled", text="Enabled", placeholder="puppet_enabled")
	col.prop(element, "property_x", text="X", placeholder="puppet_x")
	if(element.type == "2d"):
		col.prop(element, "property_y", text="Y", placeholder="puppet_y")

	col.label(text="Blendtree")
	if(not validate_stf_data_resource_reference(element.blendtree, ["stfexp.animation_blendtree"])):
		col.label(text="Create a 'stfexp.animation_blendtree' type resource in a Blender-Collection under 'STF Data Resources'.", icon="INFO_LARGE")
	col.use_property_split = True
	draw_stf_data_resource_reference(col.column(align=True), element.blendtree, ["stfexp.animation_blendtree"])
	return row


def _draw_func_blendtree(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box = layout.box()
	row = box.row(align=True)
	col = row.column(align=True)
	col.prop(element, "name")
	col.separator(factor=1, type="SPACE")

	if(not validate_stf_data_resource_reference(element, ["stfexp.animation_blendtree"])):
		col.label(text="Create a 'stfexp.animation_blendtree' type resource in a Blender-Collection under 'STF Data Resources'.", icon="INFO_LARGE")
	col.use_property_split = True
	draw_stf_data_resource_reference(col.column(align=True), element, ["stfexp.animation_blendtree"])
	return row


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: Squirrelbite_Avatar_Setup):
	layout.use_property_split = True

	header, body = layout.panel("com.squirrelbite_avatar_setup_toggles_pre", default_closed = True)
	header.label(text="Overridable Toggles (" + str(len(component.toggles_pre)) + ")")
	if(body): draw_list(body, "collection", component, "toggles_pre", _blender_property_name, _draw_func_toggle)

	header, body = layout.panel("com.squirrelbite_avatar_setup_puppets_pre", default_closed = True)
	header.label(text="Overridable Persistent Puppets (" + str(len(component.puppets_pre)) + ")")
	if(body): draw_list(body, "collection", component, "puppets_pre", _blender_property_name, _draw_func_puppet)

	layout.label(text="Expression & Face-tracking logic is processed here")

	header, body = layout.panel("com.squirrelbite_avatar_setup_toggles", default_closed = True)
	header.label(text="Toggles (" + str(len(component.toggles)) + ")")
	if(body): draw_list(body, "collection", component, "toggles", _blender_property_name, _draw_func_toggle)

	header, body = layout.panel("com.squirrelbite_avatar_setup_puppets", default_closed = True)
	header.label(text="Puppets (" + str(len(component.puppets)) + ")")
	if(body): draw_list(body, "collection", component, "puppets", _blender_property_name, _draw_func_blendtree)

	header, body = layout.panel("com.squirrelbite_avatar_setup_misc", default_closed = True)
	header.label(text="Other Animations")
	if(body):
		box = body.box()
		box.label(text="Breathing Controls")
		box.prop(component, "breathing_normal")
		box.prop(component, "breathing_intense")

		box = body.box()
		box.label(text="Additive Animations")
		box.prop(component, "additive_excited")
		box.prop(component, "additive_idle")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	component: Squirrelbite_Avatar_Setup = component
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	# toggles pre

	# puppets pre
	for puppet_json in json_resource.get("puppets_pre", []):
		puppet: PersistentPuppet = component.puppets_pre.add()
		puppet.type = puppet_json["puppet_type"]
		puppet.name = puppet_json.get("name", "")
		puppet.property_enabled = puppet_json.get("property_enabled")
		puppet.property_x = puppet_json.get("property_x")
		if(puppet.type == "2d"):
			puppet.property_y = puppet_json.get("property_x")

		if(blendtree_resource := import_resource(context, json_resource, puppet_json["blendtree"], "data")):
			puppet.blendtree.collection = context.get_root_collection()
			puppet.blendtree.stf_data_resource_id = blendtree_resource.stf_id
		else:
			context.report(STFReport("module: %s stf_id: %s, context-object: %s" % (_stf_type, stf_id, context_object), STFReportSeverity.Warn, stf_id, _stf_type, context_object))

	# toggles

	# puppets
	for puppet_json in json_resource.get("puppets", []):
		if(blendtree_resource := import_resource(context, json_resource, puppet_json["blendtree"], "data")):
			puppet: STFDataResourceReference = component.puppets.add()
			puppet.name = puppet_json.get("name", "")
			puppet.collection = context.get_root_collection()
			puppet.stf_data_resource_id = blendtree_resource.stf_id
		else:
			context.report(STFReport("module: %s stf_id: %s, context-object: %s" % (_stf_type, stf_id, context_object), STFReportSeverity.Warn, stf_id, _stf_type, context_object))

	# breathing

	# additive

	return component


def _stf_export(context: STF_ExportContext, component: Squirrelbite_Avatar_Setup, context_object: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)

	# toggles pre

	# puppets pre
	puppets_pre = []
	ret["puppets_pre"] = puppets_pre
	for puppet in component.puppets_pre:
		if(not puppet.blendtree):
			continue
		puppet: PersistentPuppet = puppet
		puppet_json = {
			"name": puppet.name,
			"puppet_type": puppet.type,
			"property_enabled": puppet.property_enabled,
			"property_x": puppet.property_x
		}
		if(puppet.type == "2d"):
			puppet_json["property_y"] = puppet.property_y

		if(puppet_ret := resolve_stf_data_resource_reference(puppet.blendtree)):
			puppet_ref, puppet_resource = puppet_ret
			if(puppet_ref.stf_type == "stfexp.animation_blendtree"):
				puppet_json["blendtree"] = register_exported_resource(ret, context.serialize_resource(puppet_resource))
				puppets_pre.append(puppet_json)
			else:
				context.report(STFReport("module: %s stf_id: %s, context-object: %s :: blendtree invalid resource type" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))
		else:
			context.report(STFReport("module: %s stf_id: %s, context-object: %s :: failed to resolve blendtree resource" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))

	# toggles

	# puppets
	puppets = []
	ret["puppets"] = puppets
	for puppet in component.puppets:
		if(puppet_ret := resolve_stf_data_resource_reference(puppet)):
			puppet_ref, puppet_resource = puppet_ret
			if(puppet_ref.stf_type == "stfexp.animation_blendtree"):
				puppets.append({
					"name": puppet.name,
					"blendtree": register_exported_resource(ret, context.serialize_resource(puppet_resource))
				})
			else:
				context.report(STFReport("module: %s stf_id: %s, context-object: %s :: blendtree invalid resource type" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))

	# breathing

	# additive

	return ret, component.stf_id


class STF_Module_Squirrelbite_Avatar_Setup(STF_BlenderComponentModule):
	"""Opinionated setup of animation logic and behaviors for VR & V-Tubing avatars"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [Squirrelbite_Avatar_Setup]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = []

	pretty_name_template = "Squirrelbite Avatar Setup"


register_stf_modules = [
	STF_Module_Squirrelbite_Avatar_Setup
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=Squirrelbite_Avatar_Setup, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
