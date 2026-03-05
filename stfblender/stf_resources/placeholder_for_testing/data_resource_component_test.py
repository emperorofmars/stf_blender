import bpy
from typing import Any

from ...common import STF_ExportContext, STF_ImportContext, STF_Category
from ...common.resource.component import STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref
from ...common.resource.component.component_utils import add_component, export_component_base, import_component_base
from ...common.blender_grr import *


_stf_type = "placeholder.remove.me.data_resource"
_blender_property_name = "stf_data_resource_component_test"


class STF_Data_Resource_Component_Test(STF_ComponentResourceBase):
	blender_reference: bpy.props.PointerProperty(type=BlenderResourceReference) # type: ignore
	data_reference: bpy.props.PointerProperty(type=STFDataResourceReference) # type: ignore
	grr: bpy.props.PointerProperty(type=BlenderGRR) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: Any, component: STF_Data_Resource_Component_Test):
	layout.use_property_split = True
	layout.label(text="Blender Ref")
	draw_blender_resource_reference(layout.column(align=True), component.blender_reference)
	layout.label(text="STF Data Ref")
	draw_stf_data_resource_reference(layout.column(align=True), component.data_reference)
	layout.label(text="GRR")
	draw_blender_grr(layout.column(align=True), component.grr)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	return component


def _stf_export(context: STF_ExportContext, component: STF_Data_Resource_Component_Test, context_object: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	return ret, component.stf_id


class Handler_Data_Resource_Component_Test(STF_Handler_Component):
	"""Placeholder Test"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = []
	understood_application_types = [STF_Data_Resource_Component_Test]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	draw_component_func = _draw_component
	filter_all_data_modules = True


register_stf_handlers = [
	Handler_Data_Resource_Component_Test
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=STF_Data_Resource_Component_Test))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
