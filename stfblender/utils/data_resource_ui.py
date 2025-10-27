import bpy

from ..base.stf_module_data import STF_BlenderDataResourceBase, STF_Data_Ref
from ..base.stf_registry import find_data_module, get_blender_non_native_data_modules
from .misc import CopyToClipboard
from .data_resource_utils import STFCreateDataResourceOperator, STFEditDataResourceOperator, STFRemoveDataResourceOperator
from .component_ui import draw_components_ui, set_stf_data_resource_component_filter
from .component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ..stf_modules.fallback.json_fallback_data import STF_Module_JsonFallbackData
from .draw_multiline_text import draw_multiline_text



class STFDrawDataResourceList(bpy.types.UIList):
	"""List of STF data-resources"""
	bl_idname = "COLLECTION_UL_stf_data_resource_list"

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse") # type: ignore
	sort_by: bpy.props.EnumProperty(items=[("original", "Added Order", "", "SORTSIZE", 0),("stf_type", "Component Type", "", "GROUP", 1),("stf_name", "Name", "", "FILE_TEXT", 2)], name="Sort by")# type: ignore
	filter_name: bpy.props.StringProperty(name="Filter Name")# type: ignore
	filter_type: bpy.props.StringProperty(name="Filter Type")# type: ignore

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_type", text="", placeholder="Filter Type", icon="FILTER")
		row.prop(self, "filter_name", text="", placeholder="Filter Name", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[STF_Data_Ref] = getattr(data, propname)

		filter = [self.bitflag_filter_item] * len(items)
		if(self.filter_name or self.filter_type):
			for idx, item in enumerate(items):
				filter_match = True
				if(self.filter_name):
					if(hasattr(item.id_data, item.blender_property_name)):
						for resource in getattr(item.id_data, item.blender_property_name):
							if(resource.stf_id == item.stf_id):
								if(not resource.stf_name or not (self.filter_name.lower() in resource.stf_name.lower() or resource.stf_name.lower() in self.filter_name.lower())):
									filter_match = False
								break
				if(self.filter_type and not (self.filter_type.lower() in item.stf_type.lower() or item.stf_type.lower() in self.filter_type.lower())):
					filter_match = False
				if(not filter_match):
					filter[idx] = ~self.bitflag_filter_item

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, STF_Data_Ref]):
			match(self.sort_by):
				case "stf_name":
					if(hasattr(item[1].id_data, item[1].blender_property_name)):
						for resource in getattr(item[1].id_data, item[1].blender_property_name):
							if(resource.stf_id == item[1].stf_id):
								return resource.stf_name
					return ""
				case "stf_type":
					return item[1].stf_type
				case _:
					return item[0]
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, self.sort_reverse)

		return filter, sortorder

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: STF_Data_Ref, icon, active_data, active_propname):
		component = None
		if(hasattr(item.id_data, item.blender_property_name)):
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
		else:
			layout.alert = True
			row_l.label(text="Invalid Resource!", icon="ERROR")

		row_r = row.row()
		row_r.alignment = "RIGHT"
		row_r.label(text=item.stf_id[:8] + "..")
		row_r.operator(CopyToClipboard.bl_idname, text="", icon="DUPLICATE", emboss=False).text = item.stf_id


def _get_data_resource_component_ref_property_collection(context: bpy.types.Context) -> any:
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


def draw_resource(layout: bpy.types.UILayout, context: bpy.types.Context, resource_ref: STF_Data_Ref, collection: bpy.types.Collection, resource: STF_BlenderDataResourceBase):
	box = layout.box()
	row = box.row()
	row.label(text=resource_ref.stf_type + "  -  ID: " + resource_ref.stf_id + " ")
	
	box = layout.box()
	# Component header info
	row = box.row()
	row_l = row.row()
	row_l.alignment = "LEFT"
	row_l.label(text=resource_ref.stf_type)
	row_r = row.row()
	row_r.alignment = "RIGHT"
	row_r.label(text="ID: " + resource_ref.stf_id)
	row_r.operator(CopyToClipboard.bl_idname, text="", icon="DUPLICATE").text = resource_ref.stf_id
	row_r.operator(STFEditDataResourceOperator.bl_idname, text="", icon="MODIFIER").resource_id = resource_ref.stf_id

	box.prop(resource, "stf_name")

	stf_modules = get_blender_non_native_data_modules()
	selected_module = None
	if(resource_ref.blender_property_name == STF_Module_JsonFallbackData.blender_property_name):
		selected_module = STF_Module_JsonFallbackData
	else:
		for stf_module in stf_modules:
			if(stf_module.stf_type == resource_ref.stf_type):
				selected_module = stf_module
				break

	if(selected_module):
		if(selected_module.__doc__):
			box.separator(factor=1, type="LINE")
			draw_multiline_text(box, selected_module.__doc__)

		if(hasattr(selected_module, "draw_resource_func")):
			box.separator(factor=1, type="LINE")
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
		row2_l = row2.row(align=True)
		if(not bpy.context.scene.stf_fallback_data_type or len(bpy.context.scene.stf_fallback_data_type) < 3 or "." not in bpy.context.scene.stf_fallback_data_type):
			row2_l.alert = True
		row2_l.prop(bpy.context.scene, "stf_fallback_data_type")
		row2_r = row2.row(align=True)
		row2_r.alignment = "RIGHT"
		if(not bpy.context.scene.stf_fallback_data_type or len(bpy.context.scene.stf_fallback_data_type) < 3 or "." not in bpy.context.scene.stf_fallback_data_type):
			row2_r.enabled = False
		add_button = row2_r.operator(STFCreateDataResourceOperator.bl_idname, icon="PLUS", text="Add Fallback Resource")
		add_button.use_scene_collection = collection == context.scene.collection
		add_button.stf_type = bpy.context.scene.stf_fallback_data_type
		add_button.property_name = selected_add_module.blender_property_name
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
	bpy.types.Scene.stf_fallback_data_type = bpy.props.StringProperty(name="Type", description="Type of unsupported resource", options=set())

def unregister():
	if hasattr(bpy.types.Scene, "stf_data_modules"):
		del bpy.types.Scene.stf_data_modules
	if hasattr(bpy.types.Scene, "stf_fallback_data_type"):
		del bpy.types.Scene.stf_fallback_data_type
