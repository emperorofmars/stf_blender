import bpy
import json

from ...base.stf_module_component import STF_Component_Ref
from ...base.stf_module_data import STF_Data_Ref
from ...base.blender_grr import BlenderGRR, draw_blender_grr


class FallbackResourcesAdd(bpy.types.Operator):
	"""Add a referenced resource"""
	bl_idname = "stf.fallback_component_resources_add"
	bl_label = "Add Reference"
	bl_options = {"REGISTER", "UNDO"}

	blender_id_property: bpy.props.StringProperty() # type: ignore
	blender_id_object: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		if(blender_id_property := getattr(bpy.data, self.blender_id_property.lower() + "s")):
			for component in getattr(blender_id_property[self.blender_id_object], self.blender_property_name):
				if(component.stf_id == self.resource_id):
					component.referenced_resources.add()
					return {"FINISHED"}
		return {"CANCELLED"}

class FallbackResourcesRemove(bpy.types.Operator):
	"""Remove a referenced resource"""
	bl_idname = "stf.fallback_component_resources_remove"
	bl_label = "Remove Reference"
	bl_options = {"REGISTER", "UNDO"}

	blender_id_property: bpy.props.StringProperty() # type: ignore
	blender_id_object: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore
	reference_index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		if(blender_id_property := getattr(bpy.data, self.blender_id_property.lower() + "s")):
			for component in getattr(blender_id_property[self.blender_id_object], self.blender_property_name):
				if(component.stf_id == self.resource_id):
					component.referenced_resources.remove(self.reference_index)
					return {"FINISHED"}
		return {"CANCELLED"}


class FallbackBuffersAdd(bpy.types.Operator):
	"""Add Buffer"""
	bl_idname = "stf.fallback_component_buffers_add"
	bl_label = "Add Buffer"
	bl_options = {"REGISTER", "UNDO"}

	blender_id_property: bpy.props.StringProperty() # type: ignore
	blender_id_object: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		if(blender_id_property := getattr(bpy.data, self.blender_id_property.lower() + "s")):
			for component in getattr(blender_id_property[self.blender_id_object], self.blender_property_name):
				if(component.stf_id == self.resource_id):
					import uuid
					buffer = component.buffers.add()
					buffer.stf_id = str(uuid.uuid4())
					return {"FINISHED"}
		return {"CANCELLED"}

class FallbackBuffersRemove(bpy.types.Operator):
	"""Remove buffer"""
	bl_idname = "stf.fallback_component_buffers_remove"
	bl_label = "Remove Buffer"
	bl_options = {"REGISTER", "UNDO"}

	blender_id_property: bpy.props.StringProperty() # type: ignore
	blender_id_object: bpy.props.StringProperty() # type: ignore
	blender_property_name: bpy.props.StringProperty() # type: ignore
	resource_id: bpy.props.StringProperty() # type: ignore
	buffer_index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		if(blender_id_property := getattr(bpy.data, self.blender_id_property.lower() + "s")):
			for component in getattr(blender_id_property[self.blender_id_object], self.blender_property_name):
				if(component.stf_id == self.resource_id):
					component.buffers.remove(self.buffer_index)
					return {"FINISHED"}
		return {"CANCELLED"}


class FallbackResourcesList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_fallback_resources_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: BlenderGRR, icon, active_data, active_propname, index):
		layout.label(text=item.reference_type)


class FallbackBuffersList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_fallback_buffers_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: BlenderGRR, icon, active_data, active_propname, index):
		layout.label(text=item.stf_id)
		layout.label(text=str(len(item.buffer_base64)))



def draw_fallback(layout: bpy.types.UILayout, resource_ref: STF_Component_Ref | STF_Data_Ref, resource: any):
	col = layout.column(align=True)
	col.label(text="Json Data:", icon="PASTEDOWN")
	json_error = False
	try:
		json_resource = json.loads(resource.json)
		if("type" not in json_resource or json_resource["type"] != resource_ref.stf_type):
			col.label(text="Invalid 'type' in Json", icon="ERROR")
			json_error = True
	except:
		col.label(text="Json Invalid", icon="ERROR")
		json_error = True
	col.alert = json_error
	col.prop(resource, "json", text="", icon="ERROR" if json_error else "NONE")

	layout.separator(factor=1)

	box = layout.box()
	box.label(text="Referenced Resources")
	row = box.row()
	row.template_list(FallbackResourcesList.bl_idname, "", resource, "referenced_resources", resource, "active_referenced_resource")
	col = row.column()
	add_resource_button = col.operator(FallbackResourcesAdd.bl_idname, text="", icon="PLUS")
	add_resource_button.resource_id = resource_ref.stf_id
	add_resource_button.blender_property_name = resource_ref.blender_property_name
	add_resource_button.blender_id_object = resource_ref.id_data.name
	add_resource_button.blender_id_property = resource_ref.id_data.id_type
	if(len(resource.referenced_resources) > 0 and len(resource.referenced_resources) > resource.active_referenced_resource):
		remove_resource_button = col.operator(FallbackResourcesRemove.bl_idname, text="", icon="X")
		remove_resource_button.reference_index = resource.active_referenced_resource
		remove_resource_button.resource_id = resource_ref.stf_id
		remove_resource_button.blender_property_name = resource_ref.blender_property_name
		remove_resource_button.blender_id_object = resource_ref.id_data.name
		remove_resource_button.blender_id_property = resource_ref.id_data.id_type

		box.use_property_split = True
		draw_blender_grr(box.column(align=True), resource.referenced_resources[resource.active_referenced_resource])

	layout.separator(factor=1)

	box = layout.box()
	box.label(text="Buffers")
	row = box.row()
	row.template_list(FallbackBuffersList.bl_idname, "", resource, "buffers", resource, "active_buffer")
	col = row.column()
	add_buffer_button = col.operator(FallbackBuffersAdd.bl_idname, text="", icon="PLUS")
	add_buffer_button.resource_id = resource_ref.stf_id
	add_buffer_button.blender_property_name = resource_ref.blender_property_name
	add_buffer_button.blender_id_object = resource_ref.id_data.name
	add_buffer_button.blender_id_property = resource_ref.id_data.id_type
	if(len(resource.buffers) > 0 and len(resource.buffers) > resource.active_buffer):
		remove_buffer_button = col.operator(FallbackBuffersRemove.bl_idname, text="", icon="X")
		remove_buffer_button.buffer_index = resource.active_buffer
		remove_buffer_button.resource_id = resource_ref.stf_id
		remove_buffer_button.blender_property_name = resource_ref.blender_property_name
		remove_buffer_button.blender_id_object = resource_ref.id_data.name
		remove_buffer_button.blender_id_property = resource_ref.id_data.id_type

		box.prop(resource.buffers[resource.active_buffer], "buffer_base64", text="Raw Base64 Data")
