import bpy

from .stf_material_definition import STF_Material_Property, STF_Material_Value_Base, STF_Material_Value_Ref
from ....utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ....utils.component_utils import STFAddComponentOperatorBase, STFEditComponentOperatorBase, STFRemoveComponentOperatorBase
from ....utils.component_ui import draw_components_ui, set_stf_component_filter
from .material_value_modules import blender_material_value_modules
from .stf_material_operators import STFAddMaterialProperty, STFAddMaterialPropertyValue, STFClearMaterial, STFRemoveMaterialProperty, STFRemoveMaterialPropertyValue
from .convert_blender_material_to_stf import STFConvertBlenderMaterialToSTF
from .convert_stf_material_to_blender import STFConvertSTFMaterialToBlender


class STFSetMaterialIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Material"""
	bl_idname = "stf.set_material_stf_id"
	@classmethod
	def poll(cls, context): return context.material is not None
	def get_property(self, context): return context.material.stf_info

class STFAddMaterialComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Material"""
	bl_idname = "stf.add_material_component"
	@classmethod
	def poll(cls, context): return context.material is not None
	def get_property(self, context): return context.material

class STFRemoveMaterialComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	"""Remove selected component from Material"""
	bl_idname = "stf.remove_material_component"
	def get_property(self, context): return context.material

class STFEditMaterialComponentIdOperator(bpy.types.Operator, STFEditComponentOperatorBase):
	"""Edit the ID of this Component"""
	bl_idname = "stf.edit_material_component_id"
	def get_property(self, context): return context.material


class STFDrawMaterialPropertyList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_material_list"

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse") # type: ignore
	sort_by: bpy.props.EnumProperty(items=[("original", "Added Order", "", "SORTSIZE", 0),("property_type", "ID", "", "NONE", 1),("value_type", "Type", "", "NONE", 2)], name="Sort by")# type: ignore
	filter_id: bpy.props.StringProperty(name="Filter Property ID")# type: ignore
	filter_type: bpy.props.EnumProperty(items=[("none", "None", "", "NONE", 0),("color", "Color", "", "COLOR", 1),("float", "Float", "", "NONE", 2),("int", "Int", "", "NONE", 3),("image", "Image", "", "IMAGE", 4)], default="none", name="Filter Type")# type: ignore

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_id", text="", placeholder="Filter ID", icon="FILTER")
		row.prop(self, "filter_type", text="", placeholder="Filter Type", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[STF_Material_Property] = getattr(data, propname)

		filter = [self.bitflag_filter_item] * len(items)
		if(self.filter_id or self.filter_type):
			for idx, item in enumerate(items):
				filter_match = True
				if(self.filter_id and not (self.filter_id.lower() in item.property_type.lower() or item.property_type.lower() in self.filter_id.lower())):
					filter_match = False
				if(self.filter_type != "none" and self.filter_type != item.value_type):
					filter_match = False
				if(not filter_match):
					filter[idx] = ~self.bitflag_filter_item

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, STF_Material_Property]):
			match(self.sort_by):
				case "property_type":
					return item[1].property_type
				case "value_type":
					print(item[1].value_type)
					return item[1].value_type
				case _:
					return item[0]
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, self.sort_reverse)
		return filter, sortorder

	def draw_item(self, context, layout, data, item: STF_Material_Property, icon, active_data, active_propname, index: int):
		alert = not item.property_type or item.property_type.strip() == ""
		layout.alert = alert
		split = layout.split(factor=0.55)
		row_l = split.row()
		row_l.alignment = "LEFT"
		row_l.label(text=item.property_type, icon="WARNING_LARGE" if alert else "NONE")
		row_r = split.row()
		row_r.label(text=item.value_type.capitalize())
		row_r.label(text=str(len(item.values)) + (" Values" if len(item.values) > 1 else " Value"))

class STFDrawMaterialPropertyValueList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_material_value_list"
	def draw_item(self, context, layout, data, item: STF_Material_Value_Ref, icon, active_data, active_propname, index: int):
		layout.label(text="Value " + str(index))


class STFMaterialHintAdd(bpy.types.Operator):
	"""Add style hint. These values can be used to determine a target shader and their settings"""
	bl_idname = "stf.material_hint_add"
	bl_label = "Add Style Hint"
	bl_options = {"REGISTER", "UNDO"}
	def execute(self, context):
		context.material.stf_material.style_hints.add()
		return {"FINISHED"}

class STFMaterialHintRemove(bpy.types.Operator):
	"""Remove style hint"""
	bl_idname = "stf.material_hint_remove"
	bl_label = "Remove Style Hint"
	bl_options = {"REGISTER", "UNDO"}
	index: bpy.props.IntProperty() # type: ignore
	def execute(self, context):
		context.material.stf_material.style_hints.remove(self.index)
		return {"FINISHED"}


class STFMaterialShaderTargetAdd(bpy.types.Operator):
	"""Define which application will parse this material into which shader. The shader names are set in the order of their priority. The first shader that exists will be used"""
	bl_idname = "stf.material_shader_target_add"
	bl_label = "Add Shader Target"
	bl_options = {"REGISTER", "UNDO"}
	def execute(self, context):
		context.material.stf_material.shader_targets.add()
		return {"FINISHED"}

class STFMaterialShaderTargetRemove(bpy.types.Operator):
	"""Remove stader target"""
	bl_idname = "stf.material_shader_target_remove"
	bl_label = "Remove Shader Target"
	bl_options = {"REGISTER", "UNDO"}
	index: bpy.props.IntProperty() # type: ignore
	def execute(self, context):
		context.material.stf_material.shader_targets.remove(self.index)
		return {"FINISHED"}

class STFMaterialShaderTargetShaderAdd(bpy.types.Operator):
	"""Add shader name to target"""
	bl_idname = "stf.material_shader_target_shader_add"
	bl_label = "Add Shader"
	bl_options = {"REGISTER", "UNDO"}
	index: bpy.props.IntProperty() # type: ignore
	def execute(self, context):
		context.material.stf_material.shader_targets[self.index].shaders.add()
		return {"FINISHED"}

class STFMaterialShaderTargetShaderRemove(bpy.types.Operator):
	"""Remove stader"""
	bl_idname = "stf.material_shader_target_shader_remove"
	bl_label = "Remove Shader"
	bl_options = {"REGISTER", "UNDO"}
	index: bpy.props.IntProperty() # type: ignore
	index_shader: bpy.props.IntProperty() # type: ignore
	def execute(self, context):
		context.material.stf_material.shader_targets[self.index].shaders.remove(self.index_shader)
		return {"FINISHED"}


class STFMaterialSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_material_spatial_editor"
	bl_label = "STF Editor: stf.material"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_context = "material"

	@classmethod
	def poll(cls, context):
		return (context.material is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Material)

		# Set ID
		draw_stf_id_ui(self.layout, context, context.material, context.material.stf_info, STFSetMaterialIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		self.layout.prop(context.material.stf_material, "stf_is_source_of_truth")

		self.layout.separator(factor=1, type="SPACE")
		row = self.layout.row()
		row.operator(STFConvertBlenderMaterialToSTF.bl_idname, icon="WARNING_LARGE" if context.material.stf_material.stf_is_source_of_truth else "NONE")
		row.operator(STFConvertSTFMaterialToBlender.bl_idname, icon="WARNING_LARGE" if not context.material.stf_material.stf_is_source_of_truth else "NONE")
		row.operator(STFClearMaterial.bl_idname, icon="WARNING_LARGE" if context.material.stf_material.stf_is_source_of_truth else "NONE")

		self.layout.separator(factor=2, type="LINE")

		# Material properties
		# TODO list properties by group, allow for custom hot-loaded code to draw entire groups, only list properties manually like this in an 'advanced view'
		self.layout.label(text="STF Material Properties")

		row = self.layout.row(align=True)
		row.prop(context.scene, "stf_material_value_modules", text="")
		row.operator(STFAddMaterialProperty.bl_idname, icon="ADD")

		# Draw List of properties
		row_property_list = self.layout.row(align=True)
		row_property_list.template_list(STFDrawMaterialPropertyList.bl_idname, "", context.material.stf_material, "properties", context.material.stf_material, "active_property_index")

		box = self.layout.box()
		box.use_property_split = True

		if(len(context.material.stf_material.properties) > context.material.stf_material.active_property_index):
			row_property_list.operator(STFRemoveMaterialProperty.bl_idname, text="", icon="X").index = context.material.stf_material.active_property_index

			# Draw property
			prop: STF_Material_Property = context.material.stf_material.properties[context.material.stf_material.active_property_index]
			property_type_row = box.row()
			if(not prop.property_type or prop.property_type.strip() == ""): property_type_row.alert = True
			property_type_row.prop(prop, "property_type", icon="WARNING_LARGE" if not prop.property_type or prop.property_type.strip() == "" else "NONE") # TODO handle understood property types
			box.prop(prop, "multi_value")

			# Draw property value(s)
			if(prop.multi_value):
				box.separator(factor=1, type="SPACE")
				row_value_list = box.row(align=True)
				row_value_list.template_list(STFDrawMaterialPropertyValueList.bl_idname, "", prop, "values", prop, "active_value_index")
			if(value := _find_value(context, prop)):
				if(prop.multi_value):
					if(len(prop.values) > 1):
						row_value_list.operator(STFRemoveMaterialPropertyValue.bl_idname, text="", icon="X").index = context.material.stf_material.active_property_index
					box.operator(STFAddMaterialPropertyValue.bl_idname).index = context.material.stf_material.active_property_index

				box.separator(factor=1, type="LINE")
				_draw_value(box, context, prop, value)
			else:
				box.operator(STFAddMaterialPropertyValue.bl_idname).index = context.material.stf_material.active_property_index

		# Hints
		self.layout.separator(factor=2, type="LINE")
		header, body = self.layout.panel("stf.material_hints", default_closed = False)
		header.label(text="Shader Hints", icon="GROUP")
		if(body):
			box = body.box()
			header_row = box.row()
			header_row_l = header_row.row()
			header_row_l.alignment = "LEFT"
			header_row_l.label(text="Style Hints")
			header_row_r = header_row.row()
			header_row_r.alignment = "RIGHT"
			header_row_r.operator(STFMaterialHintAdd.bl_idname, icon="ADD")
			if(len(context.material.stf_material.style_hints)):
				row = box.row()
				row.separator(factor=2.0)
				col = row.column(align=True)
				for style_hint_index, style_hint in enumerate(context.material.stf_material.style_hints):
					row_inner = col.row(align=True)
					alert = not style_hint.value or style_hint.value.strip() == ""
					row_inner.alert = alert
					row_inner.prop(style_hint, "value", text="", icon="WARNING_LARGE" if alert else "NONE", placeholder="realistic / cartoony / outline / etc..")
					row_inner.operator(STFMaterialHintRemove.bl_idname, text="", icon="X").index = style_hint_index

			box = body.box()
			header_row = box.row()
			header_row_l = header_row.row()
			header_row_l.alignment = "LEFT"
			header_row_l.label(text="Shader Targets")
			header_row_r = header_row.row()
			header_row_r.alignment = "RIGHT"
			header_row_r.operator(STFMaterialShaderTargetAdd.bl_idname, icon="ADD")
			if(len(context.material.stf_material.shader_targets)):
				for target_index, shader_target in enumerate(context.material.stf_material.shader_targets):
					row = box.row()
					col_outer = row.box().column()
					row_header = col_outer.row()
					row_header_l = row_header.row()
					alert = not shader_target.target or shader_target.target.strip() == ""
					row_header_l.alert = alert
					row_header_l.prop(shader_target, "target", text="Application", placeholder="blender | unity | godot | etc..", icon="WARNING_LARGE" if alert else "NONE")
					row_header_r = row_header.row()
					row_header_r.alignment = "RIGHT"
					row_header_r.operator(STFMaterialShaderTargetRemove.bl_idname, text="", icon="X").index = target_index
					row_add = col_outer.row()
					row_add.alignment = "RIGHT"
					row_add.operator(STFMaterialShaderTargetShaderAdd.bl_idname, icon="ADD").index = target_index
					col_outer.separator(factor=1.0)
					if(len(shader_target.shaders)):
						row_inner = col_outer.row()
						row_inner.separator(factor=4.0)
						col_inner = row_inner.column(align=True)
						for shader_index, shader in enumerate(shader_target.shaders):
							row_value = col_inner.row(align=True)
							alert = not shader.value or shader.value.strip() == ""
							row_value.alert = alert
							row_value.prop(shader, "value", text="", placeholder="ShaderNodeBsdfPrincipled | .poiyomi/Poiyomi Toon | etc..", icon="WARNING_LARGE" if alert else "NONE")
							btn = row_value.operator(STFMaterialShaderTargetShaderRemove.bl_idname, text="", icon="X")
							btn.index = target_index
							btn.index_shader = shader_index

		# Components
		self.layout.separator(factor=2, type="LINE")
		header, body = self.layout.panel("stf.material_components", default_closed = True)
		header.label(text="STF Components", icon="GROUP")
		if(body): draw_components_ui(self.layout, context, context.material.stf_info, context.material, STFAddMaterialComponentOperator.bl_idname, STFRemoveMaterialComponentOperator.bl_idname, STFEditMaterialComponentIdOperator.bl_idname)


def _find_value(context: bpy.types.Context, prop: STF_Material_Property):
	value_ref_index = prop.active_value_index if prop.multi_value else 0
	if(len(prop.values) <= value_ref_index):
		return None
	for value in getattr(context.material, prop.value_property_name):
		if(value.value_id == prop.values[value_ref_index].value_id):
			return value
	return None

def _draw_value(layout: bpy.types.UILayout, context: bpy.types.Context, prop: STF_Material_Property, value: STF_Material_Value_Base):
	for mat_module in blender_material_value_modules:
		if(mat_module.property_name == prop.value_property_name):
			mat_module.draw_func(layout, context, context.material, value)
			break
