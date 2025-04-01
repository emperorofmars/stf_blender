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
	if(not hasattr(bpy.types.Action, "slot_links")):
		context.report(STFReport("Slot Links are required to export animations!", STFReportSeverity.Warn, stf_id, _stf_type))
		return

	blender_animation = bpy.data.actions.new(json_resource.get("name", "STF Animation"))
	blender_animation.stf_id = stf_id
	blender_animation.use_fake_user = True
	if(json_resource.get("name")):
		blender_animation.stf_name = json_resource["name"]
		blender_animation.stf_name_source_of_truth = True

	blender_animation.use_cyclic = json_resource.get("loop", False)
	if("range" in json_resource):
		blender_animation.use_frame_range = True
		blender_animation.frame_start = json_resource["range"][0]
		blender_animation.frame_end = json_resource["range"][1]

	for track in json_resource.get("tracks", []):
		target_ret = context.resolve_stf_property_path(track.get("target", []))
		if(target_ret):
			target_object, slot_type, fcurve_target, property_index, conversion_func = target_ret

			selected_slot_link = None
			for slot_link in blender_animation.slot_links:
				if(slot_link.target == target_object):
					for slot in blender_animation.slots:
						if(slot.handle == slot_link.slot_handle):
							selected_slot_link = slot_link
							break
				if(selected_slot_link):
					break

			if(not selected_slot_link):
				blender_slot = blender_animation.slots.new(slot_type, target_object.name + " - " + slot_type)
				selected_slot_link = blender_animation.slot_links.add()
				selected_slot_link.slot_handle = blender_slot.handle
				selected_slot_link.target = target_object


			"""print()
			print(track["target"])
			print(str(target_object) + " (" + slot_type +"): " + str(fcurve_target) + " [" + str(property_index) + "] - " + str(conversion_func))"""

	return blender_animation


def _stf_export(context: STF_ExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str]:
	blender_animation: bpy.types.Action = application_object
	if(blender_animation.stf_exclude): return None
	if(blender_animation.is_action_legacy):
		context.report(STFReport("Ignoring legacy animation: " + blender_animation.name, STFReportSeverity.Warn, blender_animation.stf_id, _stf_type, application_object))
		return None
	if(not hasattr(blender_animation, "slot_links")):
		context.report(STFReport("Slot Links are required to export animations!", STFReportSeverity.Warn, blender_animation.stf_id, _stf_type, application_object))
		return None

	ensure_stf_id(context, blender_animation)

	ret = {
		"type": _stf_type,
		"name": blender_animation.stf_name if blender_animation.stf_name_source_of_truth else blender_animation.name,
		"loop": blender_animation.use_cyclic,
	}
	if(blender_animation.use_frame_range):
		ret["range"] = [blender_animation.frame_start, blender_animation.frame_end]

	stf_tracks = []

	# This is a mess.
	for layer in blender_animation.layers:
		for strip in layer.strips:
			if(strip.type == "KEYFRAME"):
				strip: bpy.types.ActionKeyframeStrip = strip
				for channelbag in strip.channelbags:
					# Get the target for this set of animation tracks from the Slot Link extension. (Why can't you be normal Blender?)
					selected_slot_link = None
					for slot_link in blender_animation.slot_links:
						if(slot_link.slot_handle == channelbag.slot_handle):
							selected_slot_link = slot_link
							break
					if(selected_slot_link):
						for fcurve in channelbag.fcurves:
							# Get bezier export import done first, then deal with other interpolation kinds and whatever else
							property_translation = context.resolve_application_property_path(selected_slot_link.target, fcurve.data_path, fcurve.array_index)

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
								context.report(STFReport("Invalid fcurve data_path: " + fcurve.data_path, STFReportSeverity.Debug, None, _stf_type, blender_animation))
					else:
						context.report(STFReport("Invalid Animation Target", STFReportSeverity.Debug, None, _stf_type, blender_animation))

	ret["tracks"] = stf_tracks

	if(len(stf_tracks) == 0):
		context.report(STFReport("Empty Animation", STFReportSeverity.Debug, None, _stf_type, blender_animation))
		return None
	else:
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
