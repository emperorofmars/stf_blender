import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.animation"


def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> tuple[any, any]:
	blender_animation = bpy.data.actions.new(json_resource.get("name", "STF Animation"))
	blender_animation.stf_id = id
	if(json_resource.get("name")):
		blender_animation.stf_name = json_resource["name"]
		blender_animation.stf_name_source_of_truth = True

	animation_context = STF_ResourceImportContext(context, json_resource, blender_animation)

	return blender_animation, animation_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_animation: bpy.types.Action = application_object
	ensure_stf_id(context, blender_animation)

	ret = {
		"type": _stf_type,
		"name": blender_animation.stf_name if blender_animation.stf_name_source_of_truth else blender_animation.name,
	}
	animation_context = STF_ResourceExportContext(context, ret, blender_animation)

	return ret, blender_animation.stf_id, animation_context


class STF_Module_STF_Animation(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["animation"]
	understood_application_types = [bpy.types.Action]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Animation
]


def register():
	bpy.types.Action.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Action.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Action.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Action.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Action.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Action, "stf_id"):
		del bpy.types.Action.stf_id
	if hasattr(bpy.types.Action, "stf_name"):
		del bpy.types.Action.stf_name
	if hasattr(bpy.types.Action, "stf_name_source_of_truth"):
		del bpy.types.Action.stf_name_source_of_truth
	if hasattr(bpy.types.Action, "stf_components"):
		del bpy.types.Action.stf_components
	if hasattr(bpy.types.Action, "stf_active_component_index"):
		del bpy.types.Action.stf_active_component_index
