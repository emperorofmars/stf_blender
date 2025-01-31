import bpy

from .stf_dependency_import import libstf, stfblender


_stf_type = "my_custom.namespaced.brush"


def _stf_import(context: libstf.stf_import_context.STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]: # type: ignore
	application_object = bpy.data.brushes.new(json_resource.get("name", "My Custom Brush"))
	application_object.stf_id = id
	if(json_resource.get("name")):
		application_object.stf_name = json_resource["name"]
		application_object.stf_name_source_of_truth = True

	resource_context = libstf.stf_import_context.STF_ResourceImportContext(context, json_resource, application_object)

	# TODO Do most of the import

	return application_object, resource_context


def _stf_export(context: libstf.stf_export_context.STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]: # type: ignore
	application_object: bpy.types.Brush = application_object
	stfblender.utils.id_utils.ensure_stf_id(context, application_object)

	json_resource = {
		"type": _stf_type,
		"name": application_object.stf_name if application_object.stf_name_source_of_truth else application_object.name,
	}
	resource_context = libstf.stf_export_context.STF_ResourceExportContext(context, json_resource, application_object)

	# TODO Do most of the export

	return json_resource, application_object.stf_id, resource_context


class CustomSTFBrushModule(libstf.stf_module.STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["brush", "or", "whatever"]
	priority = 0
	understood_application_types = [bpy.types.Brush]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = stfblender.utils.component_utils.get_components_from_object


register_stf_modules = [CustomSTFBrushModule]


def register():
	bpy.types.Brush.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Brush.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Brush.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Brush.stf_components = bpy.props.CollectionProperty(type=stfblender.utils.component_utils.STF_Component, name="Components") # type: ignore
	bpy.types.Brush.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Brush, "stf_id"):
		del bpy.types.Brush.stf_id
	if hasattr(bpy.types.Brush, "stf_name"):
		del bpy.types.Brush.stf_name
	if hasattr(bpy.types.Brush, "stf_name_source_of_truth"):
		del bpy.types.Brush.stf_name_source_of_truth
	if hasattr(bpy.types.Brush, "stf_components"):
		del bpy.types.Brush.stf_components
	if hasattr(bpy.types.Brush, "stf_active_component_index"):
		del bpy.types.Brush.stf_active_component_index
