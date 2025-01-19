import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.material"


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_material = bpy.data.materials.new(json_resource.get("name", "STF Material"))
	blender_material.stf_id = id
	blender_material.stf_name = json_resource.get("name", "STF Material")

	material_context = STF_ResourceImportContext(context, json_resource, blender_material)

	return blender_material, material_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_material: bpy.types.Material = application_object
	ensure_stf_id(context, blender_material)

	ret = {
		"type": _stf_type,
		"name": blender_material.name
	}
	material_context = STF_ResourceExportContext(context, ret, blender_material)

	return ret, blender_material.stf_id, material_context


class STF_Module_STF_Material(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["material"]
	understood_application_types = [bpy.types.Material]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Material
]


def register():
	bpy.types.Material.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Material.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Material.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Material.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Material, "stf_id"):
		del bpy.types.Material.stf_id
	if hasattr(bpy.types.Material, "stf_name"):
		del bpy.types.Material.stf_name
	if hasattr(bpy.types.Material, "stf_components"):
		del bpy.types.Material.stf_components
	if hasattr(bpy.types.Material, "stf_active_component_index"):
		del bpy.types.Material.stf_active_component_index
