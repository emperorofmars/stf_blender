import bpy

from ..base.stf_module_data import STF_BlenderDataResourceBase, STF_Data_Ref
from ..base.stf_registry import find_data_module, get_blender_non_native_data_modules
from .misc import CopyToClipboard
from .data_resource_utils import STFCreateDataResourceOperator, STFEditDataResourceOperator, STFRemoveDataResourceOperator
from .component_ui import draw_components_ui, set_stf_data_resource_component_filter
from .component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from .draw_multiline_text import draw_multiline_text


def _get_data_resource_component_ref_property_collection(context) -> any:
	for resource in getattr(context.scene.collection if stf_data_resource_use_scene_collection else context.collection, stf_data_resource_property):
		if(resource.stf_id == stf_data_resource_id):
			return resource.stf_components

class STFAddDataResourceComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Data-Resource"""
	bl_idname = "stf.add_data_resource_component"
	@classmethod
	def poll(cls, context): return context.scene is not None if stf_data_resource_use_scene_collection else context.collection is not None
	def get_property(self, context): return context.scene.collection if stf_data_resource_use_scene_collection else context.collection
	def get_components_ref_property(self, context) -> any: return _get_data_resource_component_ref_property_collection(context)

class STFRemoveDataResourceComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Data-Resource"""
	bl_idname = "stf.remove_data_resource_component"
	@classmethod
	def poll(cls, context): return context.scene is not None if stf_data_resource_use_scene_collection else context.collection is not None
	def get_property(self, context): return context.scene.collection if stf_data_resource_use_scene_collection else context.collection
	def get_components_ref_property(self, context) -> any: return _get_data_resource_component_ref_property_collection(context)

class STFEditDataResourceComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID and overrides of this component"""
	bl_idname = "stf.edit_data_resource_component_id"
	@classmethod
	def poll(cls, context): return context.scene is not None if stf_data_resource_use_scene_collection else context.collection is not None
	def get_property(self, context): return context.scene.collection if stf_data_resource_use_scene_collection else context.collection
	def get_components_ref_property(self, context) -> any: return _get_data_resource_component_ref_property_collection(context)


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
	row.operator(CopyToClipboard.bl_idname, text="Copy ID", icon="DUPLICATE").text = resource_ref.stf_id
	edit_button = row.operator(STFEditDataResourceOperator.bl_idname, text="Edit ID", icon="MODIFIER")
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
			draw_multiline_text(box, selected_module.__doc__)
			

		if(hasattr(selected_module, "draw_resource_func")):
			selected_module.draw_resource_func(box, context, resource_ref, collection, resource)
		else:
			pass

		# Components
		set_stf_data_resource_component_filter(type(resource))
		set_stf_data_resource_property(collection == context.scene.collection, resource_ref.blender_property_name, resource_ref.stf_id)
		layout.separator(factor=1, type="SPACE")
		header, body = layout.panel(resource_ref.stf_type + "_components", default_closed = False)
		header.label(text=resource_ref.stf_type + " Components", icon="GROUP")
		if(body): draw_components_ui(layout, context, resource, collection, STFAddDataResourceComponentOperator.bl_idname, STFRemoveDataResourceComponentOperator.bl_idname, STFEditDataResourceComponentIdOperator.bl_idname, is_data_resource_component=True)
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
	selected_add_module = find_data_module(get_blender_non_native_data_modules(), context.scene.stf_data_modules)

	if(selected_add_module and selected_add_module.stf_type == None): # Fallback
		row2 = layout.row(align=True)
		row2.label(text="Manually specify type") # todo
	elif(selected_add_module):
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


stf_data_resource_property = None
stf_data_resource_id = None
stf_data_resource_use_scene_collection = False
def set_stf_data_resource_property(use_scene_collection: bool, blender_property: str, resource_id: str):
	global stf_data_resource_use_scene_collection
	stf_data_resource_use_scene_collection = use_scene_collection
	global stf_data_resource_property
	stf_data_resource_property = blender_property
	global stf_data_resource_id
	stf_data_resource_id = resource_id


def _build_stf_data_resource_types_enum_callback(self, context) -> list:
	return [((stf_module.stf_type, stf_module.stf_type, stf_module.__doc__ if stf_module.__doc__ else "")) for stf_module in get_blender_non_native_data_modules()] + [("fallback", "Json Fallback", "Manual fallback for unsupported types")]

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
