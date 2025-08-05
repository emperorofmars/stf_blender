import bpy

from .component_utils import STF_Component_Ref, find_component_module, get_component_modules
from .minsc import CopyToClipboard


class STFDrawComponentList(bpy.types.UIList):
	"""List of STF components"""
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, stf_application_object: any, component: any, edit_op: str, inject_ui = None):
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

	row = box.row()
	row.operator(CopyToClipboard.bl_idname, text="Copy ID").text = component_ref.stf_id
	row.operator(edit_op, text="Edit ID & Overrides").component_id = component_ref.stf_id

	box.prop(component, "stf_name")
	box.prop(component, "enabled")
	box.separator(factor=1, type="LINE")

	stf_modules = get_component_modules()
	selected_module = None
	for stf_module in stf_modules:
		if(stf_module.stf_type == component_ref.stf_type):
			selected_module = stf_module
			break

	if(selected_module):
		if(hasattr(selected_module, "draw_component_instance_func")):
			selected_module.draw_component_instance_func(box, context, component_ref, stf_application_object, component)
		elif(hasattr(selected_module, "draw_component_func")):
			selected_module.draw_component_func(box, context, component_ref, stf_application_object, component)
		else:
			pass
	else:
		box.label(text="Unknown Type")
		box.label(text="Blender Property Name: " + component_ref.blender_property_name)


def draw_components_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		component_holder: any,
		add_component_op: str,
		remove_component_op: str,
		edit_component_id_op: str,
		components_ref_property: any = None,
		get_target_object_func: any = None,
		inject_ui: any = None
		):
	stf_modules = get_component_modules()

	if(not components_ref_property):
		components_ref_property = component_holder

	layout.label(text="Components", icon="GROUP")

	row = layout.row(align=True)
	row.prop(bpy.context.scene, "stf_component_modules", text="")
	selected_add_module = find_component_module(stf_modules, context.scene.stf_component_modules)
	if(len(stf_modules) > 0):
		if(selected_add_module):
			add_button = row.operator(add_component_op)
			add_button.stf_type = context.scene.stf_component_modules
			add_button.property_name = selected_add_module.blender_property_name
		else:
			row.separator(factor=1)
			row.label(text="Please select a component type")

		row = layout.row(align=True)
		row.template_list(STFDrawComponentList.bl_idname, "", components_ref_property, "stf_components", components_ref_property, "stf_active_component_index")
		if(len(components_ref_property.stf_components) > components_ref_property.stf_active_component_index):
			component_ref = components_ref_property.stf_components[components_ref_property.stf_active_component_index]

			remove_button = row.operator(remove_component_op, icon="X", text="")
			remove_button.index = components_ref_property.stf_active_component_index
			remove_button.property_name = component_ref.blender_property_name

			if(hasattr(component_holder, component_ref.blender_property_name)):
				for component in getattr(component_holder, component_ref.blender_property_name):
					if(component.stf_id == component_ref.stf_id):
						target_object = component_holder
						if(get_target_object_func):
							target_object = get_target_object_func(component_holder, component_ref)
						draw_component(layout, context, component_ref, target_object, component, edit_component_id_op, inject_ui)
						break
			else:
				layout.label(text="Invalid Component: " + component_ref.blender_property_name)
	else:
		layout.label(text="No Components For This Type Available")


def draw_instance_standin_components_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		component_holder: any,
		edit_component_id_op: str,
		components_ref_property: any = None,
		get_target_object_func: any = None,
		inject_ui: any = None
		):
	stf_modules = get_component_modules()

	if(not components_ref_property):
		components_ref_property = component_holder

	row = layout.row()
	if(len(stf_modules) > 0):
		row = layout.row()
		row.template_list(STFDrawComponentList.bl_idname, "", components_ref_property, "stf_components", components_ref_property, "stf_active_component_index")
		if(len(components_ref_property.stf_components) > components_ref_property.stf_active_component_index):
			component_ref = components_ref_property.stf_components[components_ref_property.stf_active_component_index]

			if(hasattr(component_holder, component_ref.blender_property_name)):
				for component in getattr(component_holder, component_ref.blender_property_name):
					if(component.stf_id == component_ref.stf_id):
						target_object = component_holder
						if(get_target_object_func):
							target_object = get_target_object_func(component_holder, component_ref)
						draw_component(layout, context, component_ref, target_object, component, edit_component_id_op, inject_ui)
						break
			else:
				layout.label(text="Invalid Component: " + component_ref.blender_property_name)
	else:
		layout.label(text="No Components For This Type Available")


stf_component_filter = None
def set_stf_component_filter(filter = None):
	global stf_component_filter
	stf_component_filter = filter


def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, "")) for stf_module in get_component_modules(stf_component_filter)]

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

def unregister():
	if hasattr(bpy.types.Scene, "stf_component_modules"):
		del bpy.types.Scene.stf_component_modules
