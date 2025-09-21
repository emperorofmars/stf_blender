import bpy

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base
from ...blender_grr.blender_resource_reference import BlenderResourceReference, draw_blender_resource_reference


_stf_type = "placeholder.remove.me.data_resource"
_blender_property_name = "stf_data_resource_component_test"


class STF_Data_Resource_Component_Test(STF_BlenderComponentBase):
	blender_reference: bpy.props.PointerProperty(type=BlenderResourceReference) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STF_Data_Resource_Component_Test):
	layout.use_property_split = True
	layout.label(text="Foo")
	draw_blender_resource_reference(layout, component.blender_reference)


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	return component


def _stf_export(context: STF_ExportContext, component: STF_Data_Resource_Component_Test, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	return ret, component.stf_id


class STF_Module_STF_Data_Resource_Component_Test(STF_BlenderComponentModule):
	"""Placeholder Test"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = []
	understood_application_types = [STF_Data_Resource_Component_Test]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_STF_Data_Resource_Component_Test
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=STF_Data_Resource_Component_Test))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
