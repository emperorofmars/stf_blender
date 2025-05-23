import bpy

from .stf_material_definition import STF_Material_Property, STF_Material_Value_Base, STF_Material_Value_Ref
from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ...utils.component_utils import STFAddComponentOperatorBase, STFRemoveComponentOperatorBase
from ...utils.component_ui_utils import draw_components_ui, set_stf_component_filter
from .material_value_modules import blender_material_value_modules
from .stf_material_operators import STFAddMaterialProperty, STFAddMaterialPropertyValue, STFClearMaterial, STFRemoveMaterialProperty, STFRemoveMaterialPropertyValue
from .convert_blender_material_to_stf import STFConvertBlenderMaterialToSTF
from .convert_stf_material_to_blender import STFConvertSTFMaterialToBlender


class STFSetMaterialIDOperator(bpy.types.Operator, STFSetIDOperatorBase):
	"""Set STF-ID for Material"""
	bl_idname = "stf.set_material_stf_id"
	@classmethod
	def poll(cls, context): return context.material is not None
	def get_property(self, context): return context.material

class STFAddMaterialComponentOperator(bpy.types.Operator, STFAddComponentOperatorBase):
	"""Add Component to Material"""
	bl_idname = "stf.add_material_component"
	@classmethod
	def poll(cls, context): return context.material is not None
	def get_property(self, context): return context.material

class STFRemoveMaterialComponentOperator(bpy.types.Operator, STFRemoveComponentOperatorBase):
	bl_idname = "stf.remove_material_component"
	def get_property(self, context): return context.material

class STFDrawMaterialPropertyList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_material_list"
	def draw_item(self, context, layout, data, item: STF_Material_Property, icon, active_data, active_propname, index: int):
		layout.label(text=item.property_type + " (" + item.value_type + ")")

class STFDrawMaterialPropertyValueList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stf_material_value_list"
	def draw_item(self, context, layout, data, item: STF_Material_Value_Ref, icon, active_data, active_propname, index: int):
		layout.label(text="Value " + str(index))


class STFMaterialSpatialPanel(bpy.types.Panel):
	"""STF options & export helper"""
	bl_idname = "OBJECT_PT_stf_material_spatial_editor"
	bl_label = "STF Material Editor"
	bl_region_type = "WINDOW"
	bl_space_type = "PROPERTIES"
	bl_category = "STF"
	bl_context = "material"

	@classmethod
	def poll(cls, context):
		return (context.material is not None)

	def draw(self, context):
		set_stf_component_filter(bpy.types.Material)

		self.layout.label(text="stf.material")

		# Set ID
		draw_stf_id_ui(self.layout, context, context.material, STFSetMaterialIDOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		# Components
		draw_components_ui(self.layout, context, context.material, STFAddMaterialComponentOperator.bl_idname, STFRemoveMaterialComponentOperator.bl_idname)

		self.layout.separator(factor=2, type="LINE")

		self.layout.prop(context.material, "stf_is_source_of_truth")

		row = self.layout.row()
		row.operator(STFConvertBlenderMaterialToSTF.bl_idname)
		row.operator(STFConvertSTFMaterialToBlender.bl_idname)
		row.operator(STFClearMaterial.bl_idname)

		# STF Material Properties
		self.layout.prop(context.material.stf_material, "style_hints")

		# TODO list properties by group, allow for custom hot-loaded code to draw entire groups, only list properties like that which don't have a recognized group

		# Draw List of ungrouped properties
		row_property_list = self.layout.row()
		row_property_list.template_list(STFDrawMaterialPropertyList.bl_idname, "", context.material, "stf_material_properties", context.material, "stf_active_material_property_index")

		row = self.layout.row(align=True)
		row.prop(context.scene, "stf_material_value_modules", text="")
		row.operator(STFAddMaterialProperty.bl_idname, icon="ADD")

		self.layout.separator(factor=2, type="SPACE")

		if(len(context.material.stf_material_properties) > context.material.stf_active_material_property_index):
			row_property_list.operator(STFRemoveMaterialProperty.bl_idname, text="", icon="X").index = context.material.stf_active_material_property_index

			# Draw property
			prop: STF_Material_Property = context.material.stf_material_properties[context.material.stf_active_material_property_index]
			self.layout.prop(prop, "property_type") # TODO handle understood property types
			self.layout.prop(prop, "multi_value")

			# Draw property value(s)
			if(prop.multi_value):
				self.layout.separator(factor=1, type="SPACE")
				row_value_list = self.layout.row()
				row_value_list.template_list(STFDrawMaterialPropertyValueList.bl_idname, "", prop, "values", prop, "active_value_index")
			if(value := _find_value(context, prop)):
				if(prop.multi_value):
					if(len(prop.values) > 1):
						row_value_list.operator(STFRemoveMaterialPropertyValue.bl_idname, text="", icon="X").index = context.material.stf_active_material_property_index
					self.layout.operator(STFAddMaterialPropertyValue.bl_idname).index = context.material.stf_active_material_property_index

				self.layout.separator(factor=1, type="SPACE")
				_draw_value(self.layout, context, prop, value)
			else:
				self.layout.operator(STFAddMaterialPropertyValue.bl_idname).index = context.material.stf_active_material_property_index
		else:
			self.layout.label(text="Invalid Property")


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
