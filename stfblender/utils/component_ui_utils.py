import bpy

from ..core.stf_registry import get_stf_modules
from .component_utils import STF_BlenderComponentModule, STF_Component_Ref


class STFDrawComponentList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


class CopyComponentIdToClipboard(bpy.types.Operator):
	"""Copy Component Id to Clipboard"""
	bl_idname = "stf.copy_component_id_to_clipboard"
	bl_label = "Copy to Clipboard"
	bl_options = {"REGISTER", "UNDO"}

	id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		bpy.context.window_manager.clipboard = self.id
		return {"FINISHED"}


def get_component_modules(filter = None) -> list[STF_BlenderComponentModule]:
	ret = []
	for stf_module in get_stf_modules(bpy.context.preferences.addons.keys()):
		if(isinstance(stf_module, STF_BlenderComponentModule) or hasattr(stf_module, "blender_property_name") and hasattr(stf_module, "filter")):
			if(hasattr(stf_module, "filter") and filter):
				if(filter in getattr(stf_module, "filter")):
					ret.append(stf_module)
				else:
					continue
			else:
				ret.append(stf_module)
	return ret


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, stf_application_object: any, component: any, edit_op: str, inject_ui = None):
	box = layout.box()
	box.label(text=component_ref.stf_type)
	#box.label(text=component_ref.stf_type + " ( " + component_ref.stf_id + " )")
	row = box.row()
	row.label(text="ID: " + component_ref.stf_id)
	row.operator(CopyComponentIdToClipboard.bl_idname, text="Copy").id = component_ref.stf_id

	if(component.overrides):
		box.label(text="Overrides:")
		for override in component.overrides:
			row = box.row()
			row.label(text="ID: " + override.target_id)
	else:
		box.label(text="No Overrides")

	edit_button = box.operator(edit_op, text="Edit ID & Overrides")
	edit_button.component_id = component_ref.stf_id

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
		if(inject_ui):
			inject_ui(box, context, component_ref, stf_application_object, component)
		if(hasattr(selected_module, "draw_component_func")):
			selected_module.draw_component_func(box, context, component_ref, stf_application_object, component)
		else:
			pass
	else:
		box.label(text="Unknown Type")
		box.label(text="Blender Property Name: " + component_ref.blender_property_name)


def find_component_module(stf_modules: list[STF_BlenderComponentModule], stf_type: str) -> STF_BlenderComponentModule:
	for stf_module in stf_modules:
		if(stf_module.stf_type == stf_type):
			return stf_module


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

	row = layout.row()
	row.prop(bpy.context.scene, "stf_component_modules", text="")
	selected_add_module = find_component_module(stf_modules, context.scene.stf_component_modules)
	if(len(stf_modules) > 0):
		if(selected_add_module):
			add_button = row.operator(add_component_op)
			add_button.stf_type = context.scene.stf_component_modules
			add_button.property_name = selected_add_module.blender_property_name

		row = layout.row()
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


stf_component_filter = None
def set_stf_component_filter(filter = None):
	global stf_component_filter
	stf_component_filter = filter


def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, "")) for stf_module in get_component_modules(stf_component_filter)]

def register():
	bpy.types.Scene.stf_component_modules = bpy.props.EnumProperty(
		items=_build_stf_component_types_enum_callback,
		name="STF Component Types",
		description="Default & hot-loaded STF component types",
		options={"SKIP_SAVE"},
		default=None,
		get=None,
		set=None,
		update=None,
	)

def unregister():
	if hasattr(bpy.types.Scene, "stf_component_modules"):
		del bpy.types.Scene.stf_component_modules
