from typing import Callable
import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....base.stf_module import STF_Module
from ....base.stf_report import STFReportSeverity, STFReport
from ....utils.component_utils import get_components_from_object
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister
from ....utils.id_utils import ensure_stf_id


_stf_type = "stf.animation"


class STF_Animation(bpy.types.PropertyGroup):
	exclude: bpy.props.BoolProperty(name="Exclude from STF export", default=False) # type: ignore
	bake: bpy.props.BoolProperty(name="Bake Animation on Export", default=False) # type: ignore
	fps_override: bpy.props.BoolProperty(name="FPS Override", default=False) # type: ignore
	fps: bpy.props.FloatProperty(name="FPS", default=30) # type: ignore


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	if(not hasattr(bpy.types.Action, "slot_links")):
		context.report(STFReport("Slot-Link is required to import animations!", STFReportSeverity.Warn, stf_id, _stf_type))
		return

	blender_animation = bpy.data.actions.new(json_resource.get("name", "STF Animation"))
	blender_animation.stf_info.stf_id = stf_id
	blender_animation.use_fake_user = True
	if(json_resource.get("name")):
		blender_animation.stf_info.stf_name = json_resource["name"]
		blender_animation.stf_info.stf_name_source_of_truth = True

	fps = json_resource.get("fps", 30)
	if(fps != bpy.context.scene.render.fps):
		blender_animation.stf_animation.fps_override = True
		blender_animation.stf_animation.fps = fps

	blender_animation.use_cyclic = json_resource.get("loop", False)
	if("range" in json_resource):
		blender_animation.use_frame_range = True
		blender_animation.frame_start = json_resource["range"][0]
		blender_animation.frame_end = json_resource["range"][1]

	blender_animation.stf_animation.bake = json_resource.get("bake_on_export", False)

	# All of this is a mess

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
						if(slot.handle == slot_link.slot_handle and slot.target_id_type == slot_type):
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
					# Only import full unbaked keyframes
					is_source_keyframe = True if stf_keyframe and len(stf_keyframe) > 1 and type(stf_keyframe[0]) == bool and stf_keyframe[0] else False
					if(stf_keyframe and len(stf_keyframe) == 5): # todo legacy, remove at some point
						keyframe = fcurve.keyframe_points.insert(timepoint, stf_keyframe[0] if not conversion_func else conversion_func(stf_index, stf_keyframe[0]))
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[1]
						keyframe.handle_left.y = keyframe.co.y + stf_keyframe[2]
						keyframe.handle_right.x = keyframe.co.x + stf_keyframe[3]
						keyframe.handle_right.y = keyframe.co.y + stf_keyframe[4]
					elif(is_source_keyframe and len(stf_keyframe) == 6):
						keyframe = fcurve.keyframe_points.insert(timepoint, stf_keyframe[1] if not conversion_func else conversion_func(stf_index, stf_keyframe[1]))
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[2]
						keyframe.handle_left.y = keyframe.co.y + stf_keyframe[3]
						keyframe.handle_right.x = keyframe.co.x + stf_keyframe[4]
						keyframe.handle_right.y = keyframe.co.y + stf_keyframe[5]
					elif(is_source_keyframe and len(stf_keyframe) == 2):
						keyframe = fcurve.keyframe_points.insert(timepoint, stf_keyframe[1] if not conversion_func else conversion_func(stf_index, stf_keyframe[1]))
					# else keyframe is baked and can be ignored

			fcurve.keyframe_points.handles_recalc()

	return blender_animation


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_animation: bpy.types.Action = application_object
	if(blender_animation.stf_animation.exclude): return None
	if(blender_animation.is_action_legacy):
		context.report(STFReport("Ignoring legacy animation: " + blender_animation.name, STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, application_object))
		return None
	if(not hasattr(blender_animation, "slot_links")):
		context.report(STFReport("Slot-Link is required to export animations!", STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, application_object))
		return None

	for slot_link in blender_animation.slot_links:
		if(slot_link.target):
			single_slotlink_valid = True
			break
	else:
		context.report(STFReport("No valid Slot Link target specified!", STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, application_object))
		return None

	ensure_stf_id(context, blender_animation)

	ret = {
		"type": _stf_type,
		"name": blender_animation.stf_info.stf_name if blender_animation.stf_info.stf_name_source_of_truth else blender_animation.name,
		"loop": blender_animation.use_cyclic,
		"fps": bpy.context.scene.render.fps if not blender_animation.stf_animation.fps_override else blender_animation.animation.stf_fps,
		"bake_on_export": blender_animation.stf_animation.bake
	}
	if(blender_animation.use_frame_range):
		ret["range"] = [blender_animation.frame_start, blender_animation.frame_end]
	else:
		ret["range"] = [blender_animation.frame_range[0], blender_animation.frame_range[1]]

	# todo enable users to select how to deal with interpolation & baking in more detail

	stf_tracks = []

	# All of this is a mess

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
						# Yay we can finally deal with curves

						# Sort collect curves belonging together. I.e. curves animating the x, y, z positions under the same data_path
						kurwas: dict[str, dict[int, bpy.types.FCurve]] = dict()
						for fcurve in channelbag.fcurves:
							if(fcurve.data_path not in kurwas):
								kurwas[fcurve.data_path] = {fcurve.array_index: fcurve}
							else:
								kurwas[fcurve.data_path][fcurve.array_index] = fcurve

						for data_path, fcurves in kurwas.items():
							fcurve.update()

							# See if this data_path can be exported
							property_translation = context.resolve_application_property_path(selected_slot_link.target, selected_slot_link.datablock_index, data_path)
							if(property_translation):
								target, conversion_func, index_conversion = property_translation
								if(not index_conversion):
									index_conversion = []
									for _, fcurve in fcurves.items():
										if(fcurve):
											index_conversion.append(fcurve.array_index)

								stf_track: list = []
								#current_timepoint, keyframes = find_next_keyframe(ret["range"][0] - 1)
								current_timepoint, keyframes = __find_next_keyframe(ret["range"][0] - 1, blender_animation, fcurves, ret["range"][1], index_conversion, conversion_func)
								while current_timepoint != None:
									stf_track.append({
										"frame": current_timepoint,
										"values": keyframes
									})
									current_timepoint, keyframes = __find_next_keyframe(current_timepoint, blender_animation, fcurves, ret["range"][1], index_conversion, conversion_func)
									#current_timepoint, keyframes = find_next_keyframe(current_timepoint)
								stf_tracks.append({
									"target": target,
									"keyframes": stf_track
								})
							else:
								context.report(STFReport("Invalid FCurve data_path: " + fcurve.data_path, STFReportSeverity.Debug, None, _stf_type, blender_animation))
					else:
						context.report(STFReport("Invalid Animation Target", STFReportSeverity.Debug, None, _stf_type, blender_animation))

	ret["tracks"] = stf_tracks

	if(len(stf_tracks) == 0):
		context.report(STFReport("Empty Animation", STFReportSeverity.Debug, None, _stf_type, blender_animation))
		return None
	else:
		return ret, blender_animation.stf_info.stf_id


def __find_next_keyframe(last_timepoint: float, blender_animation: bpy.types.Action, fcurves: dict[int, bpy.types.FCurve], max_range: float, index_conversion: list[int], conversion_func: Callable[[int, any], any] = None) -> tuple[list | None]:
	from math import inf
	closest_timepoint = inf
	keyframes: list[list | None] = [None] * len(index_conversion)
	success = False
	# Find the point in time where one of the curves on the same data_path has the next keyframe
	for _, fcurve in fcurves.items():
		for keyframe in fcurve.keyframe_points:
			if(keyframe.co.x > (last_timepoint + 0.001) and keyframe.co.x < closest_timepoint):
				closest_timepoint = keyframe.co.x
				success = True
				break
	if(success):
		# If the next keyframe is further that one frame, and if desired, bake the values instead
		if(blender_animation.stf_animation.bake and closest_timepoint > last_timepoint + 1.001):
			closest_timepoint = last_timepoint + 1
			for _, fcurve in fcurves.items():
				keyframes[index_conversion[fcurve.array_index]] = [False, conversion_func(index_conversion[fcurve.array_index], fcurve.evaluate(closest_timepoint)) if conversion_func else fcurve.evaluate(closest_timepoint)]
		else: # Export normal full keyframe
			for _, fcurve in fcurves.items():
				for keyframe in fcurve.keyframe_points:
					if(keyframe.co.x < (closest_timepoint + 0.001) and keyframe.co.x > (closest_timepoint - 0.001)):
						# todo figure out tangents more properly
						keyframes[index_conversion[fcurve.array_index]] = [True,
							conversion_func(index_conversion[fcurve.array_index], keyframe.co.y) if conversion_func else keyframe.co.y,
							keyframe.handle_left.x - keyframe.co.x,
							keyframe.handle_left.y - keyframe.co.y,
							keyframe.handle_right.x - keyframe.co.x,
							keyframe.handle_right.y - keyframe.co.y
						]
						break
				else:
					# If one of the curves for this data_path doesn't contain a keyframe, bake it if desired
					if(blender_animation.stf_animation.bake):
						keyframes[index_conversion[fcurve.array_index]] = [False, conversion_func(index_conversion[fcurve.array_index], fcurve.evaluate(closest_timepoint)) if conversion_func else fcurve.evaluate(closest_timepoint)]
	elif(blender_animation.stf_animation.bake and last_timepoint < max_range + 0.001):
		# If no more keyframes are present, but the animation ends after the last_timepoint, bake if desired
		success = True
		closest_timepoint = last_timepoint + 1
		for _, fcurve in fcurves.items():
			keyframes[index_conversion[fcurve.array_index]] = [False, conversion_func(index_conversion[fcurve.array_index], fcurve.evaluate(closest_timepoint)) if conversion_func else fcurve.evaluate(closest_timepoint)]
	return closest_timepoint if success else None, keyframes


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
	bpy.types.Action.stf_animation = bpy.props.PointerProperty(type=STF_Animation)

def unregister():
	if hasattr(bpy.types.Action, "stf_animation"):
		del bpy.types.Action.stf_animation
	boilerplate_unregister(bpy.types.Action, "data")
