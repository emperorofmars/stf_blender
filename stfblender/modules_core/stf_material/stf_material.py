import struct
import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STF_Report_Severity, STFReport
from ...utils.component_utils import STF_Component, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.material"


def _stf_import(context: STF_RootImportContext, json: dict, id: str, parent_application_object: any) -> any:
	pass


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_material: bpy.types.Material = application_object
	ensure_stf_id(blender_material)

	stf_mesh = {
		"type": _stf_type,
		"name": blender_material.name
	}

	return stf_mesh, blender_material.stf_id, context


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
	bpy.types.Material.stf_components = bpy.props.CollectionProperty(type=STF_Component, name="Components") # type: ignore
	bpy.types.Material.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Material, "stf_id"):
		del bpy.types.Material.stf_id
	if hasattr(bpy.types.Material, "stf_components"):
		del bpy.types.Material.stf_components
	if hasattr(bpy.types.Material, "stf_active_component_index"):
		del bpy.types.Material.stf_active_component_index

