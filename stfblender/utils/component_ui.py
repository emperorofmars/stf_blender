import bpy

from ..base.stf_module_component import STF_Component_Ref
from ..base.stf_registry import get_component_modules
from .component_utils import find_component_module
from .minsc import CopyToClipboard
from .draw_multiline_text import draw_multiline_text


class STFDrawComponentList(bpy.types.UIList):
	"""List of STF components"""
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


class STFDrawInstanceComponentList(bpy.types.UIList):
	"""List of STF component instances"""
	bl_idname = "COLLECTION_UL_stf_instance_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type + " ( " + item.bone + " )")
		layout.label(text=item.stf_id)


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, stf_application_object: any, component: any, edit_op: str, is_instance: bool, inject_ui = None):
	box = layout.box()
	row = box.row()
	row.label(text=component_ref.stf_type + "  -  ID: " + component_ref.stf_id + " ")

	if(inject_ui):
		if(not inject_ui(box, context, component_ref, stf_application_object, component)):
			return

	if(component.overrides):
		box.label(text="Overrides:")
		row_inner = box.row()
		row_inner.separator(factor=2.0)
		col = row_inner.column()
		for override in component.overrides:
			col.label(text=override.target_id)

	row = row.row()
	row.alignment = "RIGHT"
	row.operator(CopyToClipboard.bl_idname, text="Copy ID").text = component_ref.stf_id
	row.operator(edit_op, text="Edit ID & Overrides").component_id = component_ref.stf_id

	row = box.row()
	row_l = row.row()
	row_l.alignment = "LEFT"
	row_l.prop(component, "enabled")
	row.separator(factor=5)
	row.prop(component, "stf_name")
	box.separator(factor=1, type="LINE")

	stf_modules = get_component_modules()
	selected_module = None
	for stf_module in stf_modules:
		if(stf_module.stf_type == component_ref.stf_type):
			selected_module = stf_module
			break

	if(selected_module):
		if(selected_module.__doc__):
			draw_multiline_text(box, selected_module.__doc__)

		if(is_instance and hasattr(selected_module, "draw_component_instance_func")):
			selected_module.draw_component_instance_func(box, context, component_ref, stf_application_object, component)
		elif(not is_instance and hasattr(selected_module, "draw_component_func")):
			selected_module.draw_component_func(box, context, component_ref, stf_application_object, component)
		else:
			pass
	else:
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
		get_target_object_func: any = None,
		inject_ui: any = None,
		is_data_resource_component: bool = False
		):
	stf_modules = get_component_modules()

	available_component_modules = context.scene.stf_data_resource_component_modules if is_data_resource_component else context.scene.stf_component_modules

	row = layout.row(align=True)
	if(is_data_resource_component):
		row.prop(bpy.context.scene, "stf_data_resource_component_modules", text="")
	else:
		row.prop(bpy.context.scene, "stf_component_modules", text="")

	selected_add_module = find_component_module(stf_modules, available_component_modules)
	if(len(stf_modules) > 0):
		if(selected_add_module):
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
		get_target_object_func: any = None,
		inject_ui: any = None
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

stf_data_resource_component_filter = None
def set_stf_data_resource_component_filter(filter = None):
	global stf_data_resource_component_filter
	stf_data_resource_component_filter = filter

def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_component_modules(stf_component_filter)]

def _build_stf_data_resource_component_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_component_modules(stf_data_resource_component_filter)]

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

def unregister():
	if hasattr(bpy.types.Scene, "stf_data_resource_component_modules"):
		del bpy.types.Scene.stf_data_resource_component_modules
	if hasattr(bpy.types.Scene, "stf_component_modules"):
		del bpy.types.Scene.stf_component_modules
