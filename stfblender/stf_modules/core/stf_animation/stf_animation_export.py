from io import BytesIO
from typing import Callable
import bpy

from .stf_animation_common import *
from .stf_animation_bake import bake_constraints
from ....exporter.stf_export_context import STF_ExportContext
from ....base.stf_report import STFReportSeverity, STFReport
from ....base.stf_task_steps import STF_TaskSteps
from ....utils.id_utils import ensure_stf_id
from ....utils.buffer_utils import serialize_float


_stf_type = stf_animation_type


def stf_animation_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_animation: bpy.types.Action = application_object
	if(blender_animation.stf_animation.exclude): return None
	if(blender_animation.is_action_legacy):
		context.report(STFReport("Ignoring legacy animation: " + blender_animation.name, STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, application_object))
		return None
	if(not hasattr(blender_animation, "slot_link")):
		context.report(STFReport("Slot-Link is required to export animations!", STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, application_object))
		return None
	if(blender_animation.stf_animation.is_baked_from):
		return None # Ignore baked animations, always rebake

	for slot_link in blender_animation.slot_link.links:
		if(slot_link.target):
			break
	else:
		context.report(STFReport("No valid Slot Link target specified!", STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, application_object))
		return None

	animation_range = [blender_animation.frame_start, blender_animation.frame_end] if blender_animation.use_frame_range else [blender_animation.frame_range[0], blender_animation.frame_range[1]]

	stf_tracks, requires_constraint_bake = __convert(context, blender_animation, animation_range)
	stf_tracks_baked = None
	if(requires_constraint_bake and blender_animation.stf_animation.constraint_bake != "nobake" or blender_animation.stf_animation.constraint_bake == "bake"):
		baked = bake_constraints(blender_animation)
		stf_tracks_baked, _ = __convert(context, baked, animation_range)
		def _clean_baked():
			bpy.data.actions.remove(baked)
		context.add_cleanup_task(_clean_baked)

	if(len(stf_tracks) == 0):
		context.report(STFReport("Empty Animation", STFReportSeverity.Debug, None, _stf_type, blender_animation))
		return None
	else:
		ensure_stf_id(context, blender_animation)
		ret = {
			"type": _stf_type,
			"name": blender_animation.stf_info.stf_name if blender_animation.stf_info.stf_name_source_of_truth else blender_animation.name,
			"loop": "cycle" if blender_animation.use_cyclic else "none", # todo create ui for this setting
			"fps": bpy.context.scene.render.fps if not blender_animation.stf_animation.fps_override else blender_animation.animation.stf_fps,
			"range": animation_range,
			"tracks": stf_tracks,
		}
		if(stf_tracks_baked):
			ret["tracks_baked"] = stf_tracks_baked

		def _handle_reset_animation():
			if(blender_animation.slot_link.is_reset_animation):
				ret["is_reset_animation"] = True
			elif(blender_animation.slot_link.reset_animation):
				if(reset_animation_id := context.serialize_resource(blender_animation.slot_link.reset_animation)):
					ret["reset_animation"] = reset_animation_id
		context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle_reset_animation)

		return ret, blender_animation.stf_info.stf_id


def __convert(context: STF_ExportContext, blender_animation: bpy.types.Action, animation_range: list[float]) -> tuple[list, bool]:
	# All of this is a mess
	stf_tracks = []
	requires_constraint_bake = False
	for layer in blender_animation.layers:
		for strip in layer.strips:
			if(strip.type == "KEYFRAME"):
				strip: bpy.types.ActionKeyframeStrip = strip
				for channelbag in strip.channelbags:
					# Get the target for this set of animation tracks from the Slot Link extension. (Why can't you be normal Blender?)
					selected_slot_link = None
					for slot_link in blender_animation.slot_link.links:
						if(slot_link.slot_handle == channelbag.slot_handle):
							selected_slot_link = slot_link
							break
					if(selected_slot_link):
						# Yay we can finally deal with curves

						# Collect curves belonging together. I.e. curves animating the x, y, z positions under the same data_path
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
							if(not property_translation):
								context.report(STFReport("Could not convert animated property", STFReportSeverity.Debug, blender_animation.stf_info.stf_id, _stf_type, blender_animation))
								continue

							if(property_translation.constraints): requires_constraint_bake = True

							index_conversion = property_translation.index_conversion
							if(not index_conversion):
								index_conversion = []
								for _, fcurve in fcurves.items():
									if(fcurve):
										index_conversion.append(fcurve.array_index)

							interpolation, timepoints, sub_tracks = __serialize_subtracks(context, blender_animation, fcurves, animation_range, index_conversion, property_translation.convert_func)

							stf_tracks.append({
								"target": property_translation.stf_path_part,
								"timepoints": timepoints,
								"subtracks": sub_tracks,
								"interpolation": interpolation,
							})
					else:
						context.report(STFReport("Invalid Animation Target", STFReportSeverity.Debug, None, _stf_type, blender_animation))
	return stf_tracks, requires_constraint_bake


def __serialize_subtracks(context: STF_ExportContext, blender_animation: bpy.types.Action, fcurves: dict[int, bpy.types.FCurve], animation_range: list[float], index_conversion: list[int], conversion_func: Callable[[list[float]], list[float]] = None) -> tuple[str, list, list]:
	real_timepoints_set: set[float] = set()
	# for each subtrack (i.e. the x,y,z components of a location), determine at which times have a keyframe at any of these subtracks
	for _, fcurve in fcurves.items():
		for keyframe in fcurve.keyframe_points:
			real_timepoints_set.add(keyframe.co.x)
	real_timepoints = list(real_timepoints_set)
	real_timepoints.sort()

	# Set empty track objects
	ret: list[dict | None] = [None] * len(index_conversion)
	for _, fcurve in fcurves.items():
		ret[index_conversion[fcurve.array_index]] = {"keyframes": []}

	interpolation: str = None

	# Bake values
	baked_values: list[BytesIO | None] = [None] * len(index_conversion)
	# Create buffer for each subtrack
	for _, fcurve in fcurves.items():
		baked_values[index_conversion[fcurve.array_index]] = BytesIO()

	for timepoint in range(int(animation_range[0]), int(animation_range[1] + 1)):
		value_convert = [None] * len(index_conversion)
		# Get evaluated value from each subtrack
		for _, fcurve in fcurves.items():
			value_convert[fcurve.array_index] = fcurve.evaluate(timepoint)
		# Convert value
		value_convert = conversion_func(value_convert) if conversion_func else value_convert
		# Write buffers
		for _, fcurve in fcurves.items():
			baked_values[index_conversion[fcurve.array_index]].write(serialize_float(value_convert[index_conversion[fcurve.array_index]], 4))
	# Serialize buffers for each subtrack
	for _, fcurve in fcurves.items():
		if(ret[index_conversion[fcurve.array_index]]):
			ret[index_conversion[fcurve.array_index]]["baked"] = context.serialize_buffer(baked_values[index_conversion[fcurve.array_index]].getbuffer())

	# Convert keyframes
	keyframe_indices: list[int] = [0] * len(index_conversion)
	for real_timepoint in real_timepoints:
		value_convert: list[float] = [None] * len(index_conversion)
		left_tangent_convert: list[float] = [0] * len(index_conversion)
		right_tangent_convert: list[float] = [0] * len(index_conversion)

		# Gather value from subtracks
		for _, fcurve in fcurves.items():
			# If is real keyframe, get source of truth values
			if(fcurve.keyframe_points[keyframe_indices[fcurve.array_index]].co.x == real_timepoint):
				keyframe = fcurve.keyframe_points[keyframe_indices[fcurve.array_index]]
				value_convert[fcurve.array_index] = keyframe.co.y
				left_tangent_convert[fcurve.array_index] = keyframe.handle_left.y
				right_tangent_convert[fcurve.array_index] = keyframe.handle_right.y
			else:
				# If one of the curves for this data_path doesn't contain a keyframe when the others do, bake it, regardles of the `bake` setting
				value_convert[fcurve.array_index] = fcurve.evaluate(real_timepoint)

		# Convert values
		value_convert = conversion_func(value_convert) if conversion_func else value_convert
		left_tangent_convert = conversion_func(left_tangent_convert) if conversion_func else left_tangent_convert
		right_tangent_convert = conversion_func(right_tangent_convert) if conversion_func else right_tangent_convert

		# Write keyframes for subtracks
		for _, fcurve in fcurves.items():
			# If is real keyframe, write source of truth values
			if(fcurve.keyframe_points[keyframe_indices[fcurve.array_index]].co.x == real_timepoint):
				keyframe = fcurve.keyframe_points[keyframe_indices[fcurve.array_index]]
				prev_keyframe = fcurve.keyframe_points[keyframe_indices[fcurve.array_index] - 1] if keyframe_indices[fcurve.array_index] > 0 else None
				next_keyframe = fcurve.keyframe_points[keyframe_indices[fcurve.array_index] + 1] if keyframe_indices[fcurve.array_index] + 1 < len(fcurve.keyframe_points) else None

				if(not interpolation):
					interpolation = keyframe.interpolation
				elif(keyframe.interpolation != interpolation):
					interpolation = "mixed"

				stf_keyframe = [
					True, # is source of truth, false because it's baked
					value_convert[index_conversion[fcurve.array_index]], #value
				]

				left_tangent = None
				if(prev_keyframe and prev_keyframe.interpolation == "BEZIER"):
					left_frame_offset = keyframe.co.x - prev_keyframe.co.x
					left_tangent_factor = max(abs((keyframe.handle_left.x - keyframe.co.x) / left_frame_offset), 1)
					left_tangent = [[(keyframe.handle_left.x - keyframe.co.x) / left_tangent_factor, (value_convert[index_conversion[fcurve.array_index]] - left_tangent_convert[index_conversion[fcurve.array_index]]) / left_tangent_factor]] # left tangent values relative to keyframe

				if(keyframe.interpolation == "BEZIER"):
					right_tangent_factor = 1
					if(next_keyframe):
						right_frame_offset = next_keyframe.co.x - keyframe.co.x
						right_tangent_factor = max(abs((keyframe.handle_right.x - keyframe.co.x) / right_frame_offset), 1)

					stf_keyframe += [
						"bezier", # interpolation type
						handle_type_to_stf.get(keyframe.handle_right_type, "split"), # tangent type
						[(keyframe.handle_right.x - keyframe.co.x) / right_tangent_factor, (value_convert[index_conversion[fcurve.array_index]] - right_tangent_convert[index_conversion[fcurve.array_index]]) / right_tangent_factor], # right tangent values relative to keyframe
					]
				elif(keyframe.interpolation == "CONSTANT"):
					stf_keyframe.append("constant")
				elif(keyframe.interpolation == "LINEAR"):
					stf_keyframe.append("linear")
				elif(keyframe.interpolation == "QUAD"):
					stf_keyframe.append("quadratic")
				elif(keyframe.interpolation == "CUBIC"):
					stf_keyframe.append("cubic")

				if(left_tangent):
					stf_keyframe = stf_keyframe + left_tangent

				# todo more interpolation types, for sure cubic & quatratic

				# Finally write the stf_keyframe
				ret[index_conversion[fcurve.array_index]]["keyframes"].append(stf_keyframe)

				keyframe_indices[fcurve.array_index] += 1
			else:
				# If one of the curves for this data_path doesn't contain a keyframe when the others do, bake it, regardles of the `bake` setting
				ret[index_conversion[fcurve.array_index]]["keyframes"].append([
					False, # is source of truth, false because it's baked
					keyframe.co.x, # frame number
					value_convert[index_conversion[fcurve.array_index]], #value
				]) # don't add the left tangent at all, since this is not a real keyframe

	match(interpolation):
		case "mixed": interpolation = "mixed"
		case "BEZIER": interpolation = "bezier"
		case "CONSTANT": interpolation = "constant"
		case "LINEAR": interpolation = "linear"
		case "QUAD": interpolation = "quadratic"
		case "CUBIC": interpolation = "cubic"
		case _: interpolation = "unknown"

	return interpolation, real_timepoints, ret

