import bpy
from typing import Callable

from .component_utils import AddOverrideToComponent, RemoveOverrideFromComponent
from ..base.stf_module_component import InstanceModComponentRef, STF_BlenderComponentBase, STF_Component_Ref
from ..base.stf_registry import find_component_module, get_all_component_modules, get_component_modules, get_data_component_modules
from ..base.blender_grr import *
from .misc import CopyToClipboard
from .draw_multiline_text import draw_multiline_text
from ..stf_modules.fallback.json_fallback_component import STF_Module_JsonFallbackComponent


class STFDrawComponentList(bpy.types.UIList):
	"""List of STF components"""
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data: STF_Component_Ref, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


class STFDrawInstanceComponentList(bpy.types.UIList):
	"""List of STF component instances"""
	bl_idname = "COLLECTION_UL_stf_instance_component_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: InstanceModComponentRef, icon, active_data, active_propname):
		layout.label(text=item.stf_type + " ( " + item.bone + " )", icon="PROP_ON" if item.override else "PROP_OFF")
		layout.label(text=item.stf_id)


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, stf_application_object: any, component: STF_BlenderComponentBase, edit_op: str, is_instance: bool, inject_ui: Callable = None):
	box = layout.box()
	# Component header info
	row = box.row()
	row_l = row.row()
	row_l.alignment = "LEFT"
	row_l.label(text=component_ref.stf_type)
	row_r = row.row()
	row_r.alignment = "RIGHT"
	row_r.label(text="ID: " + component_ref.stf_id)
	row_r.operator(CopyToClipboard.bl_idname, text="", icon="DUPLICATE").text = component_ref.stf_id
	row_r.operator(edit_op, text="", icon="MODIFIER").component_id = component_ref.stf_id

	# enabled & name
	row = box.row()
	row_l = row.row()
	row_l.alignment = "LEFT"
	row_l.prop(component, "enabled")
	row.separator(factor=5)
	row.prop(component, "stf_name")

	# overrides
	header, body = box.panel("stf.component_overrides_" + str(component_ref.stf_type) + str(component_ref.stf_id) + str(is_instance), default_closed = True)
	header.label(text="Component Overrides (" + str(len(component.overrides)) + ")", icon="COPY_ID")
	if(body):
		overrides_box = body.box()
		row = overrides_box.row()
		row_l = row.row(); row_l.alignment = "LEFT"; row_l.label(text="Overrides:")
		row_r = row.row(); row_r.alignment = "RIGHT"; add_button = row_r.operator(AddOverrideToComponent.bl_idname, icon="PLUS")
		add_button.blender_id_type = component.id_data.id_type
		add_button.blender_property_name = component_ref.blender_property_name
		if(type(stf_application_object) == bpy.types.Bone):
			add_button.bone_name = stf_application_object.name
		add_button.component_id = component_ref.stf_id

		overrides_box.use_property_split = True
		for index, override in enumerate(component.overrides):
			row = overrides_box.row()
			draw_blender_grr(row.column(align=True), override, "stf_component")
			remove_button = row.operator(RemoveOverrideFromComponent.bl_idname, text="", icon="X")
			remove_button.blender_id_type = component.id_data.id_type
			remove_button.blender_property_name = component_ref.blender_property_name
			if(type(stf_application_object) == bpy.types.Bone):
				remove_button.bone_name = stf_application_object.name
			remove_button.component_id = component_ref.stf_id
			remove_button.index = index

	# relevant for component instances & standins
	if(inject_ui):
		box.separator(factor=1, type="LINE")
		if(not inject_ui(box, context, component_ref, stf_application_object, component)):
			return

	# determine the components module and call its appropriate draw function
	stf_modules = get_all_component_modules()
	selected_module = None
	if(component_ref.blender_property_name == STF_Module_JsonFallbackComponent.blender_property_name):
		selected_module = STF_Module_JsonFallbackComponent
	else:
		for stf_module in stf_modules:
			if(stf_module.stf_type == component_ref.stf_type):
				selected_module = stf_module
				break

	if(selected_module):
		if(selected_module.__doc__):
			box.separator(factor=1, type="LINE")
			draw_multiline_text(box, selected_module.__doc__)

		if(is_instance and hasattr(selected_module, "draw_component_instance_func")):
			box.separator(factor=1, type="LINE")
			selected_module.draw_component_instance_func(box, context, component_ref, stf_application_object, component)
		elif(not is_instance and hasattr(selected_module, "draw_component_func")):
			box.separator(factor=1, type="LINE")
			selected_module.draw_component_func(box, context, component_ref, stf_application_object, component)
		else:
			pass
	else:
		box.separator(factor=1, type="LINE")
		box.label(text="Unknown Type")
		box.label(text="Blender Property Name: " + component_ref.blender_property_name)


def draw_components_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		ref_holder: any,
		component_holder: any,
		add_component_op: str,
		remove_component_op: str,
		edit_component_id_op: str,
		get_target_object_func: Callable = None,
		inject_ui: any = None,
		is_data_resource_component: bool = False,
		is_component_instance: bool = False
		):
	stf_modules = get_data_component_modules() if is_data_resource_component else get_component_modules()

	row = layout.row(align=True)
	# let available_component_modules
	if(is_data_resource_component):
		available_component_modules = context.scene.stf_data_resource_component_modules
		row.prop(bpy.context.scene, "stf_data_resource_component_modules", text="")
	elif(is_component_instance):
		available_component_modules = context.scene.stf_component_instance_modules
		row.prop(bpy.context.scene, "stf_component_instance_modules", text="")
	else:
		available_component_modules = context.scene.stf_component_modules
		row.prop(bpy.context.scene, "stf_component_modules", text="")

	selected_add_module = find_component_module(stf_modules, available_component_modules)
	if(selected_add_module and selected_add_module.stf_type == None): # Fallback
		row2 = layout.row(align=True)
		row2_l = row2.row(align=True)
		if(not bpy.context.scene.stf_fallback_component_type or len(bpy.context.scene.stf_fallback_component_type) < 3 or "." not in bpy.context.scene.stf_fallback_component_type):
			row2_l.alert = True
		row2_l.prop(bpy.context.scene, "stf_fallback_component_type")
		row2_r = row2.row(align=True)
		row2_r.alignment = "RIGHT"
		if(not bpy.context.scene.stf_fallback_component_type or len(bpy.context.scene.stf_fallback_component_type) < 3 or "." not in bpy.context.scene.stf_fallback_component_type):
			row2_r.enabled = False
		add_button = row2_r.operator(add_component_op, icon="PLUS", text="Add Fallback Component")
		add_button.stf_type = bpy.context.scene.stf_fallback_component_type
		add_button.property_name = selected_add_module.blender_property_name
	elif(selected_add_module):
		row_l = row.row(align=True)
		row_l.alignment = "RIGHT"
		add_button = row_l.operator(add_component_op, icon="PLUS", text="Add Component")
		add_button.stf_type = available_component_modules
		add_button.property_name = selected_add_module.blender_property_name
	else:
		row.separator(factor=1)
		row.label(text="Please select a component type")

	row = layout.row(align=True)
	row.template_list(STFDrawComponentList.bl_idname, "", ref_holder, "stf_components", ref_holder, "stf_active_component_index")
	if(len(ref_holder.stf_components) > ref_holder.stf_active_component_index):
		component_ref = ref_holder.stf_components[ref_holder.stf_active_component_index]

		remove_button = row.operator(remove_component_op, icon="X", text="")
		remove_button.index = ref_holder.stf_active_component_index
		remove_button.property_name = component_ref.blender_property_name

		if(hasattr(component_holder, component_ref.blender_property_name)):
			for component in getattr(component_holder, component_ref.blender_property_name):
				if(component.stf_id == component_ref.stf_id):
					target_object = component_holder
					if(get_target_object_func):
						target_object = get_target_object_func(component_holder, component_ref)
					draw_component(layout, context, component_ref, target_object, component, edit_component_id_op, False, inject_ui)
					break
		else:
			layout.label(text="Invalid Component: " + component_ref.blender_property_name)
	else:
		layout.label(text="No Components For This Type Available")


def draw_instance_standin_components_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		ref_holder: any,
		component_holder: any,
		edit_component_id_op: str,
		get_target_object_func: Callable = None,
		inject_ui: Callable = None
		):
	stf_modules = get_component_modules()

	row = layout.row()
	if(len(stf_modules) > 0):
		row = layout.row()
		row.template_list(STFDrawInstanceComponentList.bl_idname, "", ref_holder, "stf_components", ref_holder, "stf_active_component_index")
		if(len(ref_holder.stf_components) > ref_holder.stf_active_component_index):
			component_ref = ref_holder.stf_components[ref_holder.stf_active_component_index]

			if(hasattr(component_holder, component_ref.blender_property_name)):
				for component in getattr(component_holder, component_ref.blender_property_name):
					if(component.stf_id == component_ref.stf_id):
						target_object = component_holder
						if(get_target_object_func):
							target_object = get_target_object_func(component_holder, component_ref)
						draw_component(layout, context, component_ref, target_object, component, edit_component_id_op, True, inject_ui)
						break
			else:
				layout.label(text="Invalid Component: " + component_ref.blender_property_name)
	else:
		layout.label(text="No Components For This Type Available")


stf_component_filter = None
def set_stf_component_filter(filter = None):
	global stf_component_filter
	stf_component_filter = filter


stf_component_instance_filter = None
def set_stf_component_instance_filter(filter = None):
	global stf_component_instance_filter
	stf_component_instance_filter = filter

stf_data_resource_component_filter = None
def set_stf_data_resource_component_filter(filter = None):
	global stf_data_resource_component_filter
	stf_data_resource_component_filter = filter

def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_component_modules(stf_component_filter)] + [("fallback", "Json Fallback", "Manual fallback for unsupported types")]

def _build_stf_component_instance_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_component_modules(stf_component_instance_filter)] + [("fallback", "Json Fallback", "Manual fallback for unsupported types")]

def _build_stf_data_resource_component_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_data_component_modules(stf_data_resource_component_filter)] + [("fallback", "Json Fallback", "Manual fallback for unsupported types")]

def register():
	bpy.types.Scene.stf_component_modules = bpy.props.EnumProperty(
		items=_build_stf_component_types_enum_callback,
		name="Available STF Components",
		description="Select STF component to add",
		options={"SKIP_SAVE"},
		default=None,
		get=None,
		set=None,
		update=None,
	)
	bpy.types.Scene.stf_component_instance_modules = bpy.props.EnumProperty(
		items=_build_stf_component_instance_types_enum_callback,
		name="Available STF Components",
		description="Select STF component to add",
		options={"SKIP_SAVE"},
		default=None,
		get=None,
		set=None,
		update=None,
	)
	bpy.types.Scene.stf_data_resource_component_modules = bpy.props.EnumProperty(
		items=_build_stf_data_resource_component_types_enum_callback,
		name="Available STF Components",
		description="Select STF component to add",
		options={"SKIP_SAVE"},
		default=None,
		get=None,
		set=None,
		update=None,
	)
	bpy.types.Scene.stf_fallback_component_type = bpy.props.StringProperty(name="Type", description="Type of unsupported component", options=set())

def unregister():
	if hasattr(bpy.types.Scene, "stf_data_resource_component_modules"):
		del bpy.types.Scene.stf_data_resource_component_modules
	if hasattr(bpy.types.Scene, "stf_component_modules"):
		del bpy.types.Scene.stf_component_modules
	if hasattr(bpy.types.Scene, "stf_component_instance_modules"):
		del bpy.types.Scene.stf_component_instance_modules
	if hasattr(bpy.types.Scene, "stf_fallback_component_type"):
		del bpy.types.Scene.stf_fallback_component_type
