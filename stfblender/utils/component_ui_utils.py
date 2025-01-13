import bpy

from ...libstf.stf_registry import get_stf_modules
from .component_utils import STF_BlenderComponentModule, STF_Component


class STFDrawComponentList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_component_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


def get_component_modules(filter = None) -> list[STF_BlenderComponentModule]:
	ret = []
	for module in get_stf_modules(bpy.context.preferences.addons.keys()):
		if(isinstance(module, STF_BlenderComponentModule) or hasattr(module, "draw_component_func")):
			if(hasattr(module, "filter") and filter):
				if(filter in getattr(module, "filter")):
					ret.append(module)
				else:
					continue
			else:
				ret.append(module)
	return ret


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component, object: any, component: any):
	box = layout.box()
	box.label(text=component_ref.stf_type)
	box.label(text=component_ref.stf_id)

	modules = get_component_modules()
	selected_module = None
	for module in modules:
		if(module.stf_type == component_ref.stf_type and module.draw_component_func):
			selected_module = module
			break

	if(selected_module):
		selected_module.draw_component_func(box, context, component_ref, object, component)
	else:
		box.label(text="Unknown Type")
		box.label(text="Blender Property Name: " + component_ref.blender_property_name)


def find_component_module(modules: list[STF_BlenderComponentModule], stf_type: str) -> STF_BlenderComponentModule:
	for module in modules:
		if(module.stf_type == stf_type):
			return module


def draw_components_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		object: any,
		add_component_op: str,
		remove_component_op: str
		):
	modules = get_component_modules()

	if(context.scene.stf_component_modules):
		row = layout.row()
		row.prop(bpy.context.scene, "stf_component_modules", text="")
		selected_add_module = find_component_module(modules, context.scene.stf_component_modules)
		if(selected_add_module):
			add_button = row.operator(add_component_op)
			add_button.stf_type = context.scene.stf_component_modules
			add_button.property_name = selected_add_module.blender_property_name

		row = layout.row()
		row.template_list(STFDrawComponentList.bl_idname, "", object, "stf_components", object, "stf_active_component_index")
		if(len(object.stf_components) > object.stf_active_component_index):
			component_ref = object.stf_components[object.stf_active_component_index]

			remove_button = row.operator(remove_component_op, icon="X", text="")
			remove_button.index = object.stf_active_component_index
			remove_button.property_name = component_ref.blender_property_name

			for component in getattr(object, component_ref.blender_property_name):
				if(component.stf_id == component_ref.stf_id):
					draw_component(layout, context, component_ref, object, component)
					break


stf_component_filter = None
def set_stf_component_filter(filter: str = None):
	global stf_component_filter
	stf_component_filter = filter


def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((module.stf_type, module.stf_type, "")) for module in get_component_modules(stf_component_filter)]

def register():
	bpy.types.Scene.stf_component_modules = bpy.props.EnumProperty(
		items=_build_stf_component_types_enum_callback,
		name="STF Component Types",
		description="Default & hot-loaded STF component types",
		options={"SKIP_SAVE"},
		default=0
	)

def unregister():
	if hasattr(bpy.types.Scene, "stf_component_modules"):
		del bpy.types.Scene.stf_component_modules
