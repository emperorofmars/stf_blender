import bpy

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import get_components_from_object
from ...utils.boilerplate import boilerplate_register, boilerplate_unregister
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.animation"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> any:
	blender_animation = bpy.data.actions.new(json_resource.get("name", "STF Animation"))
	blender_animation.stf_id = stf_id
	if(json_resource.get("name")):
		blender_animation.stf_name = json_resource["name"]
		blender_animation.stf_name_source_of_truth = True

	return blender_animation


def _stf_export(context: STF_ExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str]:
	blender_animation: bpy.types.Action = application_object
	if(blender_animation.stf_exclude): return (None, None, None)
	if(blender_animation.is_action_legacy):
		context.report(STFReport("Ignoring legacy animation: " + blender_animation.name, STFReportSeverity.Warn, blender_animation.stf_id, _stf_type, application_object))
		return (None, None, None)
	if(not hasattr(blender_animation, "slot_links")):
		context.report(STFReport("Slot Links are required to export animations!", STFReportSeverity.Warn, blender_animation.stf_id, _stf_type, application_object))

	ensure_stf_id(context, blender_animation)

	ret = {
		"type": _stf_type,
		"name": blender_animation.stf_name if blender_animation.stf_name_source_of_truth else blender_animation.name,
		"loop": blender_animation.use_cyclic,
	}
	if(blender_animation.use_frame_range):
		ret["range"] = [blender_animation.frame_start, blender_animation.frame_end]


	"""print(blender_animation.name)
	print(blender_animation.is_action_legacy)
	for slot in blender_animation.slots:
		print(str(slot) + " handle: " + str(slot.handle) + " :: " + str(slot.target_id_type) + " - " + str(slot.identifier) + " - ")"""

	stf_tracks = []

	#print()
	#if(blender_animation): print("ANIM: " + blender_animation.name)

	for layer in blender_animation.layers:
		for strip in layer.strips:
			if(strip.type == "KEYFRAME"):
				strip: bpy.types.ActionKeyframeStrip = strip
				for channelbag in strip.channelbags:
					# Get the target for this set of animation tracks from the Slot Link extension. (Why can't you be normal Blender?)
					assignment = None
					for slot_link in blender_animation.slot_links:
						if(slot_link.slot_handle == channelbag.slot_handle):
							assignment = slot_link
							break
					if(assignment):
						for fcurve in channelbag.fcurves:
							# Get bezier export import done first, then deal with interpolation and whatever else
							property_translation = context.translate_application_property(slot_link.target, fcurve.data_path, fcurve.array_index)

							"""print()
							print(slot_link.target)
							print(fcurve.data_path)"""

							if(property_translation):
								target, conversion_func = property_translation

								track = []

								for keyframe in fcurve.keyframe_points:
									# TODO handles likely need to be converted from coordinates to normalized angle and weight
									track.append([keyframe.co.x, keyframe.co.y if not conversion_func else conversion_func(keyframe.co.y), keyframe.handle_left.x, keyframe.handle_left.y, keyframe.handle_right.x, keyframe.handle_right.y])

								stf_tracks.append({
									"target": target,
									"keyframes": track
								})
							else:
								pass
					else:
						#context.report(STFReport("Invalid Animation Target", STFReportSeverity.Warn, id, _stf_type, blender_animation))
						pass

	ret["tracks"] = stf_tracks

	#print()

	return ret, blender_animation.stf_id


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
	boilerplate_register(bpy.types.Action, "data")
	bpy.types.Action.stf_exclude = bpy.props.BoolProperty(name="Exclude from STF", default=False) # type: ignore

def unregister():
	boilerplate_unregister(bpy.types.Action, "data")
	if hasattr(bpy.types.Action, "stf_exclude"):
		del bpy.types.Action.stf_exclude
