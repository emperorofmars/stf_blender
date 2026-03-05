import bpy
from typing import Any

from .stf_dependency_import import stfblender


_stf_type = "my_custom.namespaced.squeak_component"
_blender_property_name = "my_custom_namespaced_squeak_component"


class SqueakComponent(stfblender.common.module_component.STF_BlenderComponentBase):
	squeak: bpy.props.BoolProperty(name="Squeak", default=True) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: stfblender.common.module_component.STF_Component_Ref, context_object: Any, component: SqueakComponent):
	layout.prop(component, "squeak")


def _stf_import(context: stfblender.common.STF_ImportContext, json_resource: dict, stf_id: str, context_object: Any) -> Any:
	component_ref, component = stfblender.common.module_component.component_utils.add_component(context_object, _blender_property_name, stf_id, _stf_type)
	ret = stfblender.common.module_component.component_utils.import_component_base(context, component, json_resource, _blender_property_name, context_object)

	component.squeak = json_resource.get("squeak", True)

	return component


def _stf_export(context: stfblender.common.STF_ExportContext, component: SqueakComponent, context_object: Any) -> tuple[dict, str]:
	ret = stfblender.common.module_component.utils.component_utils.export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret["squeak"] = component.squeak
	return ret, component.stf_id


class MyCustomSTFSqueakComponentModule(stfblender.common.module_component.STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_category = "component"
	understood_application_types = [SqueakComponent]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Collection]
	draw_component_func = _draw_component

	like_types = ["squeak"]


register_stf_modules = [MyCustomSTFSqueakComponentModule]


def register():
	bpy.utils.register_class(SqueakComponent)
	bpy.types.Object.my_custom_namespaced_squeak_component = bpy.props.CollectionProperty(type=SqueakComponent) # type: ignore
	bpy.types.Collection.my_custom_namespaced_squeak_component = bpy.props.CollectionProperty(type=SqueakComponent) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "my_custom_namespaced_squeak_component"):
		del bpy.types.Collection.my_custom_namespaced_squeak_component
	if hasattr(bpy.types.Object, "my_custom_namespaced_squeak_component"):
		del bpy.types.Object.my_custom_namespaced_squeak_component
	bpy.utils.unregister_class(SqueakComponent)
