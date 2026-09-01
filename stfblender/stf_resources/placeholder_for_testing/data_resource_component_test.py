import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....stfblender_common.blender_grr import *


class STF_Data_Resource_Component_Test(STF_ComponentResourceBase):
	blender_reference: bpy.props.PointerProperty(type=BlenderResourceReference)
	data_reference: bpy.props.PointerProperty(type=STFNonNativeResourceReference)
	grr: bpy.props.PointerProperty(type=BlenderGRR)


class Handler_Data_Resource_Component_Test(STF_Handler_Component):
	"""Placeholder Test"""
	stf_type = "placeholder.remove.me.data_resource"
	stf_category = STF_Category.COMPONENT
	understood_blender_types = [STF_Data_Resource_Component_Test]
	blender_property_name = "stf_data_resource_component_test"
	single = False
	filter_all_data_modules = True

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_Data_Resource_Component_Test):
		layout.use_property_split = True
		layout.label(text="Blender Ref")
		component.blender_reference.draw(layout.column(align=True))
		layout.label(text="STF Data Ref")
		component.data_reference.draw(layout.column(align=True))
		layout.label(text="GRR")
		component.grr.draw(layout.column(align=True))

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
		component_ref, component = add_component(context_object, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_object)
		#TODO
		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: STF_Data_Resource_Component_Test, context_object: Any) -> tuple[dict, str]:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_object)
		#TODO
		return ret, component.stf_id


def register():
	setattr(bpy.types.Collection, Handler_Data_Resource_Component_Test.blender_property_name, bpy.props.CollectionProperty(type=STF_Data_Resource_Component_Test))

def unregister():
	if hasattr(bpy.types.Collection, Handler_Data_Resource_Component_Test.blender_property_name):
		delattr(bpy.types.Collection, Handler_Data_Resource_Component_Test.blender_property_name)
