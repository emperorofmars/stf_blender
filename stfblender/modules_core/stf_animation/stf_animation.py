import bpy
from math import inf

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

	fps = json_resource.get("fps", 30)
	if(fps != bpy.context.scene.render.fps):
		blender_animation.stf_fps_override = True
		blender_animation.stf_fps = fps

	blender_animation.use_cyclic = json_resource.get("loop", False)
	if("range" in json_resource):
		blender_animation.use_frame_range = True
		blender_animation.frame_start = json_resource["range"][0]
		blender_animation.frame_end = json_resource["range"][1]

	# This is a mess.
	layer = blender_animation.layers.new("stf_layer")
	strip: bpy.types.ActionKeyframeStrip = layer.strips.new(type="KEYFRAME")

	for track in json_resource.get("tracks", []):
		target_ret = context.resolve_stf_property_path(track.get("target", []))
		if(target_ret):
			target_object, application_object_property_index, slot_type, fcurve_target, index_conversion, conversion_func = target_ret
			if(not index_conversion):
				index_conversion = []
				for track_index in range(len(track.get("keyframes", [])[0].get("values", []))):
					index_conversion.append(track_index)

			selected_slot_link = None
			selected_channelbag = None

			for slot_link in blender_animation.slot_links:
				if(slot_link.target == target_object and slot_link.datablock_index == application_object_property_index):
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
				selected_slot_link.datablock_index = application_object_property_index
				selected_channelbag = strip.channelbags.new(blender_slot)

			for slot in blender_animation.slots:
				if(slot.handle == selected_slot_link.slot_handle):
					blender_slot = slot
					break
			for channelbag in strip.channelbags:
				if(channelbag.slot_handle == blender_slot.handle):
					selected_channelbag = channelbag

			for stf_index in range(len(index_conversion)):
				fcurve: bpy.types.FCurve = selected_channelbag.fcurves.new(fcurve_target, index=index_conversion[stf_index])
				for stf_keyframes in track.get("keyframes", []):
					timepoint = stf_keyframes["frame"]
					stf_keyframe = stf_keyframes["values"][stf_index]

					keyframe = fcurve.keyframe_points.insert(timepoint, stf_keyframe[0] if not conversion_func else conversion_func(stf_index, stf_keyframe[0]))
					keyframe.handle_left.x = keyframe.co.x + stf_keyframe[1]
					keyframe.handle_left.y = keyframe.co.y + stf_keyframe[2]
					keyframe.handle_right.x = keyframe.co.x + stf_keyframe[3]
					keyframe.handle_right.y = keyframe.co.y + stf_keyframe[4]

			fcurve.keyframe_points.handles_recalc()

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
		"fps": bpy.context.scene.render.fps if not blender_animation.stf_fps_override else blender_animation.stf_fps
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
						kurwas: dict[str, dict[int, bpy.types.FCurve]] = dict()
						for fcurve in channelbag.fcurves:
							if(fcurve.data_path not in kurwas):
								kurwas[fcurve.data_path] = {fcurve.array_index: fcurve}
							else:
								kurwas[fcurve.data_path][fcurve.array_index] = fcurve

						for data_path, fcurves in kurwas.items():
							#stf_track: dict[float, list] = {}
							stf_track: list = []
							property_translation = context.resolve_application_property_path(selected_slot_link.target, selected_slot_link.datablock_index, data_path)
							if(property_translation):
								target, conversion_func, index_conversion = property_translation
								if(not index_conversion):
									index_conversion = []
									for _, fcurve in fcurves.items():
										index_conversion.append(fcurve.array_index)

								def find_next_keyframe(last_timepoint: float):
									closest_timepoint = inf
									keyframes: list[bpy.types.Keyframe] = [None] * len(index_conversion)
									success = False
									for _, fcurve in fcurves.items():
										for keyframe in fcurve.keyframe_points:
											if(keyframe.co.x > (last_timepoint + 0.001) and keyframe.co.x < closest_timepoint):
												closest_timepoint = keyframe.co.x
												success = True
												break
									if(success):
										for _, fcurve in fcurves.items():
											for keyframe in fcurve.keyframe_points:
												if(keyframe.co.x < (closest_timepoint + 0.001) and keyframe.co.x > (closest_timepoint - 0.001)):
													keyframes[fcurve.array_index] = keyframe
									return closest_timepoint if success else None, keyframes

								current_timepoint, keyframes = find_next_keyframe(-inf)
								while current_timepoint != None:
									stf_keyframes = [None] * len(index_conversion)
									# Get bezier export import done first, then deal with other interpolation kinds and whatever else
									for keyframe_index, keyframe in enumerate(keyframes):
										if(keyframe):
											stf_keyframes[index_conversion[keyframe_index]] = [
												conversion_func(keyframe_index, keyframe.co.y) if conversion_func else keyframe.co.y,
												keyframe.handle_left.x - keyframe.co.x,
												keyframe.handle_left.y - keyframe.co.y,
												keyframe.handle_right.x - keyframe.co.x,
												keyframe.handle_right.y - keyframe.co.y
											]
									#stf_track[current_timepoint] = stf_keyframes
									stf_track.append({
										"frame": current_timepoint,
										"values": stf_keyframes
									})

									current_timepoint, keyframes = find_next_keyframe(current_timepoint)

								stf_tracks.append({
									"target": target,
									"keyframes": stf_track
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
	bpy.types.Action.stf_fps_override = bpy.props.BoolProperty(name="FPS Override", default=False) # type: ignore
	bpy.types.Action.stf_fps = bpy.props.FloatProperty(name="FPS", default=30) # type: ignore

def unregister():
	boilerplate_unregister(bpy.types.Action, "data")
	if hasattr(bpy.types.Action, "stf_exclude"):
		del bpy.types.Action.stf_exclude
	if hasattr(bpy.types.Action, "stf_fps_override"):
		del bpy.types.Action.stf_fps_override
	if hasattr(bpy.types.Action, "stf_fps"):
		del bpy.types.Action.stf_fps
