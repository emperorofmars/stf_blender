import bpy
from typing import Any, Callable

from ....utils.helpers import create_add_button, create_remove_button

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "com.squirrelbite.avatar_setup"
_blender_property_name = "com_squirrelbite_avatar_setup"


class AnimationMapping(bpy.types.PropertyGroup):
	mapping: bpy.props.StringProperty(name="Mapping", options=set()) # type: ignore
	animation: bpy.props.PointerProperty(name="Animation", type=bpy.types.Action, options=set()) # type: ignore


class Toggle(bpy.types.PropertyGroup):
	animation_on: bpy.props.PointerProperty(name="On", type=bpy.types.Action, options=set()) # type: ignore
	animation_off: bpy.props.PointerProperty(name="Off", type=bpy.types.Action, options=set()) # type: ignore


class Blendtree1DAnimationMapping(bpy.types.PropertyGroup):
	position: bpy.props.FloatProperty(name="Position", default=0, soft_min=0, soft_max=1, options=set()) # type: ignore
	animation: bpy.props.PointerProperty(name="Animation", type=bpy.types.Action, options=set()) # type: ignore

class Blendtree2DAnimationMapping(bpy.types.PropertyGroup):
	position: bpy.props.FloatVectorProperty(name="Position", size=2, default=(0, 0), soft_min=-1, soft_max=1, options=set()) # type: ignore
	animation: bpy.props.PointerProperty(name="Animation", type=bpy.types.Action, options=set()) # type: ignore


class Blendtree1D(bpy.types.PropertyGroup):
	animations: bpy.props.CollectionProperty(name="Animations", type=Blendtree1DAnimationMapping, options=set()) # type: ignore

class Blendtree2D(bpy.types.PropertyGroup):
	animations: bpy.props.CollectionProperty(name="Animations", type=Blendtree2DAnimationMapping, options=set()) # type: ignore


class PersistentPuppet1D(bpy.types.PropertyGroup):
	property_enabled: bpy.props.StringProperty(name="Enabled Property", options=set()) # type: ignore
	property_x: bpy.props.StringProperty(name="Value Property", options=set()) # type: ignore
	animation: bpy.props.PointerProperty(type=Blendtree1D, options=set()) # type: ignore

class PersistentPuppet2D(bpy.types.PropertyGroup):
	property_enabled: bpy.props.StringProperty(name="Enabled Property", options=set()) # type: ignore
	property_x: bpy.props.StringProperty(name="Value Property", options=set()) # type: ignore
	property_y: bpy.props.StringProperty(name="Value Property", options=set()) # type: ignore
	animation: bpy.props.PointerProperty(type=Blendtree2D, options=set()) # type: ignore


class Squirrelbite_Avatar_Setup(STF_BlenderComponentBase):
	toggles_pre: bpy.props.CollectionProperty(name="Overridable Toggles", type=Toggle, options=set()) # type: ignore
	persistent_puppets_1d_pre: bpy.props.CollectionProperty(name="Persistent Puppets 1D", type=PersistentPuppet1D, options=set()) # type: ignore
	persistent_puppets_2d_pre: bpy.props.CollectionProperty(name="Persistent Puppets 2D", type=PersistentPuppet2D, options=set()) # type: ignore

	puppets_1d: bpy.props.CollectionProperty(name="Puppets 1D", type=Blendtree1D, options=set()) # type: ignore
	puppets_2d: bpy.props.CollectionProperty(name="Puppets 2D", type=Blendtree2D, options=set()) # type: ignore
	toggles: bpy.props.CollectionProperty(name="Toggles", type=Toggle, options=set()) # type: ignore

	breathing_normal: bpy.props.PointerProperty(name="Breathing Normal Animation", type=bpy.types.Action, options=set()) # type: ignore
	breathing_intense: bpy.props.PointerProperty(name="Breathing Intense Animation", type=bpy.types.Action, options=set()) # type: ignore

	additive_excited: bpy.props.PointerProperty(name="Additive Excited Animation", type=bpy.types.Action, options=set()) # type: ignore
	additive_idle: bpy.props.PointerProperty(name="Additive Idle Animation", type=bpy.types.Action, options=set()) # type: ignore


def draw_list(layout: bpy.types.UILayout, blender_id_type: str | bool, component: STF_BlenderComponentBase, attr: str, blender_property_name: str, draw_func: Callable):
	col = layout.column(align=True)
	for index_element, element in enumerate(getattr(component, attr)):
		layout_remove_btn = draw_func(col, element)
		create_remove_button(layout_remove_btn, blender_id_type, blender_property_name, component.stf_id, attr, index_element)
	create_add_button(layout, blender_id_type, blender_property_name, component.stf_id, attr)


def _draw_func_toggle(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box_inner = layout.box()
	row = box_inner.row(align=True)
	col = row.column(align=True)
	col.prop(element, "name")
	col.prop(element, "animation_on")
	col.prop(element, "animation_off")
	return row

def _draw_func_puppet_1d(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box_inner = layout.box()
	row = box_inner.row(align=True)
	col = row.column(align=True)
	col.prop(element, "name")
	col.prop(element, "property_enabled")
	col.prop(element, "property_x")
	col.prop(element, "animation")
	return row

def _draw_func_blendtree_1d(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box_inner = layout.box()
	row = box_inner.row(align=True)
	col = row.column(align=True)
	col.prop(element, "name")
	col.prop(element, "position")
	col.prop(element, "animation")
	return row

def _draw_func_puppet_2d(layout: bpy.types.UILayout, element: Any) -> bpy.types.UILayout:
	box_inner = layout.box()
	row = box_inner.row(align=True)
	col = row.column(align=True)
	col.prop(element, "name")
	col.prop(element, "property_enabled")
	col.prop(element, "property_x")
	col.prop(element, "property_y")
	col.prop(element, "animation")
	return row


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: Squirrelbite_Avatar_Setup):
	layout.use_property_split = True

	header, body = layout.panel("com.squirrelbite_avatar_setup_toggles_pre", default_closed = True)
	header.label(text="Overridable Toggles")
	if(body): draw_list(body, "collection", component, "toggles_pre", _blender_property_name, _draw_func_toggle)

	header, body = layout.panel("com.squirrelbite_avatar_setup_puppets_pre", default_closed = True)
	header.label(text="Overridable Persistent Puppets")
	if(body):
		box = body.box()
		box.label(text="1D")
		draw_list(box, "collection", component, "persistent_puppets_1d_pre", _blender_property_name, _draw_func_puppet_1d)
		box = body.box()
		box.label(text="2D")
		draw_list(box, "collection", component, "persistent_puppets_2d_pre", _blender_property_name, _draw_func_puppet_2d)

	layout.label(text="Expression & Face-tracking logic is processed here")

	header, body = layout.panel("com.squirrelbite_avatar_setup_toggles", default_closed = True)
	header.label(text="Toggles")
	if(body): draw_list(body, "collection", component, "toggles", _blender_property_name, _draw_func_toggle)

	header, body = layout.panel("com.squirrelbite_avatar_setup_puppets", default_closed = True)
	header.label(text="Puppets")
	if(body):
		box = body.box()
		box.label(text="1D")
		draw_list(box, "collection", component, "puppets_1d", _blender_property_name, _draw_func_puppet_1d)
		box = body.box()
		box.label(text="2D")
		draw_list(box, "collection", component, "puppets_2d", _blender_property_name, _draw_func_puppet_2d)

	header, body = layout.panel("com.squirrelbite_avatar_setup_minsc", default_closed = True)
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
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	return component


def _stf_export(context: STF_ExportContext, component: Squirrelbite_Avatar_Setup, context_object: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
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
