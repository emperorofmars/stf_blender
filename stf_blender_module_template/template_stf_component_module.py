import bpy

from .stf_dependency_import import libstf, stfblender


_stf_type = "my_custom.namespaced.squeak_component"
_blender_property_name = "my_custom_namespaced_squeak_component"


class SqueakComponent(stfblender.utils.component_utils.STF_BlenderComponentBase):
	squeak: bpy.props.BoolProperty(name="Squeak", default=True) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: stfblender.utils.component_utils.STF_BlenderComponentModule, parent_application_object: any, component: SqueakComponent): # type: ignore
	layout.prop(component, "squeak")


def _stf_import(context: libstf.stf_import_context.STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]: # type: ignore
	component_ref, component = stfblender.utils.component_utils.add_component(parent_application_object, _blender_property_name, id, _stf_type)

	component.squeak = json_resource.get("squeak", True)

	return component, context


def _stf_export(context: libstf.stf_export_context.STF_RootExportContext, application_object: SqueakComponent, parent_application_object: any) -> tuple[dict, str, any]: # type: ignore
	ret = {
		"type": _stf_type,
		"name": application_object.stf_name,
		"squeak": application_object.squeak,
	}
	return ret, application_object.stf_id, context


class MyCustomSTFSqueakComponentModule(stfblender.utils.component_utils.STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
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
