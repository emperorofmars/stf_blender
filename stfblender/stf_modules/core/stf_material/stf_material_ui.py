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
	"""Edit the ID and overrides of this Component"""
	bl_idname = "stf.edit_material_component_id"
	def get_property(self, context): return context.material


class STFDrawMaterialPropertyList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_material_list"
	def draw_item(self, context, layout, data, item: STF_Material_Property, icon, active_data, active_propname, index: int):
		layout.label(text=item.property_type + " (" + item.value_type + ")")

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

		# Components
		self.layout.separator(factor=1, type="SPACE")
		header, body = self.layout.panel("stf.material_components", default_closed = False)
		header.label(text="STF Components", icon="GROUP")
		if(body): draw_components_ui(self.layout, context, context.material.stf_info, context.material, STFAddMaterialComponentOperator.bl_idname, STFRemoveMaterialComponentOperator.bl_idname, STFEditMaterialComponentIdOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		self.layout.prop(context.material, "stf_is_source_of_truth")

		row = self.layout.row()
		row.operator(STFConvertBlenderMaterialToSTF.bl_idname)
		row.operator(STFConvertSTFMaterialToBlender.bl_idname)
		row.operator(STFClearMaterial.bl_idname)

		# STF Material Properties

		self.layout.separator(factor=2, type="LINE")
		self.layout.label(text="Style Hints")
		if(len(context.material.stf_material.style_hints)):
			row = self.layout.row()
			row.separator(factor=2.0)
			col = row.column(align=True)
			for style_hint_index, style_hint in enumerate(context.material.stf_material.style_hints):
				row_inner = col.row(align=True)
				row_inner.prop(style_hint, "value", text="")
				row_inner.operator(STFMaterialHintRemove.bl_idname, text="", icon="X").index = style_hint_index
		self.layout.operator(STFMaterialHintAdd.bl_idname)

		self.layout.separator(factor=2, type="LINE")
		self.layout.label(text="Shader Targets")
		if(len(context.material.stf_material.shader_targets)):
			row = self.layout.row()
			row.separator(factor=2.0)
			col = row.column()
			for target_index, shader_target in enumerate(context.material.stf_material.shader_targets):
				col_outer = col.column()
				row_inner = col_outer.row(align=True)
				row_inner.prop(shader_target, "target")
				row_inner.operator(STFMaterialShaderTargetRemove.bl_idname, text="", icon="X").index = target_index
				if(len(shader_target.shaders)):
					row_inner = col_outer.row()
					row_inner.separator(factor=4.0)
					col_inner = row_inner.column(align=True)
					for shader_index, shader in enumerate(shader_target.shaders):
						row_value = col_inner.row(align=True)
						row_value.prop(shader, "value", text="")
						btn = row_value.operator(STFMaterialShaderTargetShaderRemove.bl_idname, text="", icon="X")
						btn.index = target_index
						btn.index_shader = shader_index
				col_outer.operator(STFMaterialShaderTargetShaderAdd.bl_idname).index = target_index
				if(len(shader_target.shaders)):
					col_outer.separator(factor=1.0)
		self.layout.operator(STFMaterialShaderTargetAdd.bl_idname)

		self.layout.separator(factor=2, type="LINE")
		# TODO list properties by group, allow for custom hot-loaded code to draw entire groups, only list properties manually like this in an 'advanced view'
		self.layout.label(text="STF Material Properties")

		# Draw List of ungrouped properties
		row_property_list = self.layout.row(align=True)
		row_property_list.template_list(STFDrawMaterialPropertyList.bl_idname, "", context.material.stf_material, "properties", context.material.stf_material, "active_property_index")

		row = self.layout.row(align=True)
		row.prop(context.scene, "stf_material_value_modules", text="")
		row.operator(STFAddMaterialProperty.bl_idname, icon="ADD")

		self.layout.separator(factor=2, type="SPACE")

		if(len(context.material.stf_material.properties) > context.material.stf_material.active_property_index):
			row_property_list.operator(STFRemoveMaterialProperty.bl_idname, text="", icon="X").index = context.material.stf_material.active_property_index

			# Draw property
			prop: STF_Material_Property = context.material.stf_material.properties[context.material.stf_material.active_property_index]
			self.layout.prop(prop, "property_type") # TODO handle understood property types
			self.layout.prop(prop, "multi_value")

			# Draw property value(s)
			if(prop.multi_value):
				self.layout.separator(factor=1, type="SPACE")
				row_value_list = self.layout.row(align=True)
				row_value_list.template_list(STFDrawMaterialPropertyValueList.bl_idname, "", prop, "values", prop, "active_value_index")
			if(value := _find_value(context, prop)):
				if(prop.multi_value):
					if(len(prop.values) > 1):
						row_value_list.operator(STFRemoveMaterialPropertyValue.bl_idname, text="", icon="X").index = context.material.stf_material.active_property_index
					self.layout.operator(STFAddMaterialPropertyValue.bl_idname).index = context.material.stf_material.active_property_index

				self.layout.separator(factor=1, type="SPACE")
				_draw_value(self.layout, context, prop, value)
			else:
				self.layout.operator(STFAddMaterialPropertyValue.bl_idname).index = context.material.stf_material.active_property_index


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
