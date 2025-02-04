import bpy

from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.animation"


def _stf_import(context: STF_RootImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_animation = bpy.data.actions.new(json_resource.get("name", "STF Animation"))
	blender_animation.stf_id = stf_id
	if(json_resource.get("name")):
		blender_animation.stf_name = json_resource["name"]
		blender_animation.stf_name_source_of_truth = True

	animation_context = STF_ResourceImportContext(context, json_resource, blender_animation)

	return blender_animation, animation_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_animation: bpy.types.Action = application_object
	if(blender_animation.stf_exclude): return (None, None, None)
	if(blender_animation.is_action_legacy):
		context.report(STFReport("Ignoring legacy animation: " + blender_animation.name, STFReportSeverity.Warn, blender_animation.stf_id, _stf_type, application_object))
		return (None, None, None)

	ensure_stf_id(context, blender_animation)

	ret = {
		"type": _stf_type,
		"name": blender_animation.stf_name if blender_animation.stf_name_source_of_truth else blender_animation.name,
		"loop": blender_animation.use_cyclic,
	}
	if(blender_animation.use_frame_range):
		ret["range"] = [blender_animation.frame_start, blender_animation.frame_end]

	animation_context = STF_ResourceExportContext(context, ret, blender_animation)

	print(blender_animation.name)
	print(blender_animation.is_action_legacy)
	for slot in blender_animation.slots:
		print(str(slot) + " handle: " + str(slot.handle) + " :: " + str(slot.target_id_type) + " - " + str(slot.identifier) + " - ")

	for layer in blender_animation.layers:
		for strip in layer.strips:
			if(strip.type == "KEYFRAME"):
				strip: bpy.types.ActionKeyframeStrip = strip
				for channelbag in strip.channelbags:
					for target_assignment in blender_animation.stf_target_assignment:
						if(target_assignment.slot_handle != channelbag.slot_handle):
							continue

						for fcurve in channelbag.fcurves:
							#print(fcurve.data_path)
							pass

	print()

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

	bpy.types.Action.stf_exclude = bpy.props.BoolProperty(name="Exclude from STF", default=False) # type: ignore

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

	if hasattr(bpy.types.Action, "stf_exclude"):
		del bpy.types.Action.stf_exclude
