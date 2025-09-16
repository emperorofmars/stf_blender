import bpy

from ..base.stf_module_data import STF_BlenderDataModule, STF_BlenderDataResourceBase, STF_Data_Ref
from ..base.stf_registry import get_blender_non_native_data_modules
from .minsc import CopyToClipboard
from .data_resource_utils import STFCreateDataResourceOperator, STFEditDataResourceOperator, STFRemoveDataResourceOperator
from .component_ui_utils import draw_components_ui, set_stf_component_filter
from .component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase


class STFAddDataResourceComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Data-Resource"""
	bl_idname = "stf.add_data_resource_component"
	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	@classmethod
	def poll(cls, context): return context.collection is not None
	def get_property(self, context): return context.scene.collection if self.use_scene_collection else context.collection

class STFRemoveDataResourceComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Data-Resource"""
	bl_idname = "stf.remove_data_resource_component"
	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	def get_property(self, context): return context.scene.collection if self.use_scene_collection else context.collection

class STFEditDataResourceComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this Data-Resource"""
	use_scene_collection: bpy.props.BoolProperty(default=False) # type: ignore
	bl_idname = "stf.edit_data_resource_component_id"
	def get_property(self, context): return context.scene.collection if self.use_scene_collection else context.collection


def find_stf_module(stf_modules: list[STF_BlenderDataModule], stf_type: str) -> STF_BlenderDataModule:
	for stf_module in stf_modules:
		if(stf_module.stf_type == stf_type):
			return stf_module


class STFDrawDataResourceList(bpy.types.UIList):
	"""List of STF data-resources"""
	bl_idname = "COLLECTION_UL_stf_data_resource_list"

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.stf_type)
		layout.label(text=item.stf_id)


def draw_resource(layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_Data_Ref, collection: bpy.types.Collection, resource: STF_BlenderDataResourceBase):
	box = layout.box()
	row = box.row()
	row.label(text=resource_ref.stf_type + "  -  ID: " + resource_ref.stf_id + " ")

	row = row.row()
	row.alignment = "RIGHT"
	row.operator(CopyToClipboard.bl_idname, text="Copy ID").text = resource_ref.stf_id
	edit_button = row.operator(STFEditDataResourceOperator.bl_idname, text="Edit ID")
	edit_button.use_scene_collection = collection == context.scene.collection
	edit_button.resource_id = resource_ref.stf_id

	box.prop(resource, "stf_name")
	box.separator(factor=1, type="LINE")

	stf_modules = get_blender_non_native_data_modules()
	selected_module = None
	for stf_module in stf_modules:
		if(stf_module.stf_type == resource_ref.stf_type):
			selected_module = stf_module
			break

	if(selected_module):
		if(selected_module.__doc__):
			first = True
			for line in selected_module.__doc__.split("\n"):
				remaining = line
				while(len(remaining) > 80):
					box.label(text=remaining[:80], icon="INFO_LARGE" if first else "NONE")
					remaining = remaining[80:]
					first = False
				box.label(text=remaining, icon="INFO_LARGE" if first else "NONE")
				first = False

		if(hasattr(selected_module, "draw_resource_func")):
			selected_module.draw_resource_func(box, context, resource_ref, collection, resource)
		else:
			pass

		# Components
		set_stf_component_filter(type(resource))
		layout.separator(factor=1, type="SPACE")
		header, body = layout.panel(resource_ref.stf_type + "_components", default_closed = False)
		header.label(text=resource_ref.stf_type + " Components", icon="GROUP")
		if(body): draw_components_ui(layout, context, resource, context.collection, STFAddDataResourceComponentOperator.bl_idname, STFRemoveDataResourceComponentOperator.bl_idname, STFEditDataResourceComponentIdOperator.bl_idname)
	else:
		box.label(text="Unknown Type")
		box.label(text="Blender Property Name: " + resource_ref.blender_property_name)


def draw_data_resources_ui(
		layout: bpy.types.UILayout,
		context: bpy.types.Context,
		collection: bpy.types.Collection
		):
	row = layout.row(align=True)
	row.prop(bpy.context.scene, "stf_data_modules", text="")
	selected_add_module = find_stf_module(get_blender_non_native_data_modules(), context.scene.stf_data_modules)

	if(selected_add_module):
		row_l = row.row(align=True)
		row_l.alignment = "RIGHT"
		add_button = row_l.operator(STFCreateDataResourceOperator.bl_idname, icon="PLUS", text="Create Resource")
		add_button.use_scene_collection = collection == context.scene.collection
		add_button.stf_type = context.scene.stf_data_modules
		add_button.property_name = selected_add_module.blender_property_name
	else:
		row.separator(factor=1)
		row.label(text="Please select a resource type")

	row = layout.row(align=True)
	row.template_list(STFDrawDataResourceList.bl_idname, "", collection, "stf_data_refs", collection, "stf_data_ref_selected")
	if(len(collection.stf_data_refs) > collection.stf_data_ref_selected):
		resource_ref = collection.stf_data_refs[collection.stf_data_ref_selected]

		remove_button = row.operator(STFRemoveDataResourceOperator.bl_idname, icon="X", text="")
		remove_button.use_scene_collection = collection == context.scene.collection
		remove_button.index = collection.stf_data_ref_selected
		remove_button.property_name = resource_ref.blender_property_name

		if(hasattr(collection, resource_ref.blender_property_name)):
			for resource in getattr(collection, resource_ref.blender_property_name):
				if(resource.stf_id == resource_ref.stf_id):
					draw_resource(layout, context, resource_ref, collection, resource)
					break
		else:
			layout.label(text="Invalid Resource: " + resource_ref.blender_property_name)


def _build_stf_data_resource_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_blender_non_native_data_modules()]

def register():
	bpy.types.Scene.stf_data_modules = bpy.props.EnumProperty(
		items=_build_stf_data_resource_types_enum_callback,
		name="Available STF Data Modules",
		description="Select STF type of data-resource to add",
		options={"SKIP_SAVE"},
		default=None,
		get=None,
		set=None,
		update=None,
	)

def unregister():
	if hasattr(bpy.types.Scene, "stf_data_modules"):
		del bpy.types.Scene.stf_data_modules
