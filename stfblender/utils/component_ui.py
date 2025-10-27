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

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse") # type: ignore
	sort_by: bpy.props.EnumProperty(items=[("original", "Added Order", "", "SORTSIZE", 0),("stf_type", "Component Type", "", "GROUP", 1),("stf_name", "Name", "", "FILE_TEXT", 2)], name="Sort by")# type: ignore
	filter_name: bpy.props.StringProperty(name="Filter Name")# type: ignore
	filter_type: bpy.props.StringProperty(name="Filter Type")# type: ignore

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_type", text="", placeholder="Filter Type", icon="FILTER")
		global stf_component_filter
		if(stf_component_filter != bpy.types.Bone):
			row.prop(self, "filter_name", text="", placeholder="Filter Name", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[InstanceModComponentRef] = getattr(data, propname)

		filter = [self.bitflag_filter_item] * len(items)
		if(self.filter_name or self.filter_type):
			for idx, item in enumerate(items):
				filter_match = True
				if(self.filter_name):
					global stf_component_filter
					if(hasattr(item.id_data, item.blender_property_name) and stf_component_filter != bpy.types.Bone):
						for component in getattr(item.id_data, item.blender_property_name):
							if(component.stf_id == item.stf_id):
								if(not component.stf_name or not (self.filter_name.lower() in component.stf_name.lower() or component.stf_name.lower() in self.filter_name.lower())):
									filter_match = False
								break
				if(self.filter_type and not (self.filter_type.lower() in item.stf_type.lower() or item.stf_type.lower() in self.filter_type.lower())):
					filter_match = False
				if(not filter_match):
					filter[idx] = ~self.bitflag_filter_item

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, InstanceModComponentRef]):
			match(self.sort_by):
				case "stf_name":
					global stf_component_filter
					if(hasattr(item[1].id_data, item[1].blender_property_name) and stf_component_filter != bpy.types.Bone):
						for component in getattr(item[1].id_data, item[1].blender_property_name):
							if(component.stf_id == item[1].stf_id):
								return component.stf_name
					return ""
				case "stf_type":
					return item[1].stf_type
				case _:
					return item[0]
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, self.sort_reverse)

		return filter, sortorder

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: STF_Component_Ref, icon, active_data, active_propname):
		global stf_component_filter
		component = None
		if(hasattr(item.id_data, item.blender_property_name) and stf_component_filter != bpy.types.Bone):
			for component in getattr(item.id_data, item.blender_property_name):
				if(component.stf_id == item.stf_id):
					break
		split = layout.split(factor=0.4)
		split.label(text=item.stf_type, icon="GROUP")
		row = split.split(factor=0.5)
		row_l = row.row()
		if(component):
			if(component.stf_name):
				row_l.label(text=component.stf_name, icon="FILE_TEXT")
			else:
				row_l.alert = True
				row_l.label(text="Unnamed", icon="FILE_TEXT")
		elif(stf_component_filter != bpy.types.Bone):
			layout.alert = True
			row_l.label(text="Invalid Component!", icon="ERROR")

		row_r = row.row()
		row_r.alignment = "RIGHT"
		row_r.label(text=item.stf_id[:8] + "..")
		row_r.operator(CopyToClipboard.bl_idname, text="", icon="DUPLICATE", emboss=False).text = item.stf_id


class STFDrawInstanceComponentList(bpy.types.UIList):
	"""List of STF component instances"""
	bl_idname = "COLLECTION_UL_stf_instance_component_list"

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse") # type: ignore
	sort_by: bpy.props.EnumProperty(items=[("bone", "Bone", "", "BONE_DATA", 0),("stf_type", "Component Type", "", "GROUP", 1)], name="Sort by")# type: ignore
	filter_bone: bpy.props.StringProperty(name="Filter Bone")# type: ignore
	filter_type: bpy.props.StringProperty(name="Filter Type")# type: ignore

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_bone", text="", placeholder="Filter Bone", icon="FILTER")
		row.prop(self, "filter_type", text="", placeholder="Filter Type", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[InstanceModComponentRef] = getattr(data, propname)

		filter = [self.bitflag_filter_item] * len(items)
		if(self.filter_bone or self.filter_type):
			for idx, item in enumerate(items):
				filter_match = True
				if(self.filter_bone and not (self.filter_bone.lower() in item.bone.lower() or item.bone.lower() in self.filter_bone.lower())):
					filter_match = False
				if(self.filter_type and not (self.filter_type.lower() in item.stf_type.lower() or item.stf_type.lower() in self.filter_type.lower())):
					filter_match = False
				if(not filter_match):
					filter[idx] = ~self.bitflag_filter_item
			filter[idx] = ~self.bitflag_filter_item

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, InstanceModComponentRef]):
			return item[1][self.sort_by] + (item[1].stf_type if self.sort_by == "bone" else item[1].bone)
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, self.sort_reverse)

		return filter, sortorder

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: InstanceModComponentRef, icon, active_data, active_propname):
		split = layout.split(factor=0.75)
		row = split.split(factor=0.5)
		row_l = row.row()
		row_l.label(icon="CHECKMARK" if item.override else "X")
		row_l.label(text=item.bone, icon="BONE_DATA")
		row.label(text=item.stf_type, icon="GROUP")
		row_r = split.row()
		row_r.alignment = "RIGHT"
		row_r.label(text=item.stf_id[:8] + "..")
		row_r.operator(CopyToClipboard.bl_idname, text="", icon="DUPLICATE", emboss=False).text = item.stf_id


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, stf_application_object: any, component: STF_BlenderComponentBase, edit_op: str, is_instance: bool, inject_ui: Callable = None):
	box = layout.box()
	# Component header info
	row = box.row()
	row_l = row.row()
	row_l.alignment = "LEFT"
	row_l.label(text=component_ref.stf_type)
	row_r = row.row()
	row_r.alignment = "RIGHT"
	row_r.label(text="ID: " + component_ref.stf_id, icon="TAG")
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
			if(index > 0): overrides_box.separator(factor=1, type="LINE")
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
