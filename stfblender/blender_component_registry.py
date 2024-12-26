import uuid
import bpy

from ..libstf.stf_registry import get_all_stf_processors
from ..libstf.stf_processor import STF_Processor


class STF_Component(bpy.types.PropertyGroup):
	stf_type: bpy.props.StringProperty(name="Type") # type: ignore
	stf_id: bpy.props.StringProperty(name="ID") # type: ignore


class STF_Blender_Component(STF_Processor):
	draw_component_func: str
	filter: list[str]


class STFAddComponentOperatorBase:
	"""Add Component"""
	bl_label = "Add Component"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	stf_type: bpy.props.StringProperty(name="Type") # type: ignore

	def execute(self, context):
		new_item: STF_Component = self.get_property(context).stf_components.add()
		new_item.stf_id = str(uuid.uuid4())
		new_item.stf_type = self.stf_type
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


class STFRemoveComponentOperatorBase:
	bl_label = "Remove Component"
	bl_category = "STF"
	bl_options = {"REGISTER", "UNDO"}

	index: bpy.props.IntProperty(name = "component_index", default=-1) # type: ignore

	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
		self.get_property(context).stf_components.remove(self.index)
		return {"FINISHED"}

	def get_property(self, context) -> any:
		pass


def get_component_modules(filter: str = None) -> list[STF_Blender_Component]:
	ret = []
	for processor in get_all_stf_processors():
		if(isinstance(processor, STF_Blender_Component) or hasattr(processor, "draw_component_func")):
			if(hasattr(processor, "filter") and filter):
				if(filter in getattr(processor, "filter")):
					ret.append(processor)
				else:
					continue
			else:
				ret.append(processor)
	return ret


def draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component: STF_Component, object: any):
	box = layout.box()
	box.label(text=component.stf_type)
	box.label(text=component.stf_id)

	modules = get_component_modules()
	selected_module = None
	for module in modules:
		if(module.stf_type == component.stf_type and module.draw_component_func):
			selected_module = module
			break

	if(selected_module):
		selected_module.draw_component_func(box, context, component, object)
	else:
		box.label(text="Unknown Type")


def draw_component_selection(layout: bpy.types.UILayout, context: bpy.types.Context, label: str = "Select Component"):
	layout.prop(bpy.context.scene, "stf_component_modules", text=label)


def _build_stf_component_types_enum_callback(self, context) -> list:
	return [((module.stf_type, module.stf_type, "")) for module in get_component_modules()]


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
