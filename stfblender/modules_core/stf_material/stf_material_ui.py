import bpy

from .stf_material_definition import STF_Material_Property
from ...utils.id_utils import STFSetIDOperatorBase, draw_stf_id_ui
from ...utils.component_utils import STFAddComponentOperatorBase, STFRemoveComponentOperatorBase
from ...utils.component_ui_utils import draw_components_ui, set_stf_component_filter


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
	def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
		layout.label(text=item.property_type)


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

		# STF Material Properties
		self.layout.prop(context.material, "stf_is_source_of_truth")

		self.layout.prop(context.material.stf_material, "style_hints")

		self.layout.template_list(STFDrawMaterialPropertyList.bl_idname, "", context.material, "stf_material_properties", context.material, "stf_active_material_property_index")
