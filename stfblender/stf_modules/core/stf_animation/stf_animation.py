from io import BytesIO
from typing import Callable
import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....base.stf_module import STF_Module
from ....base.stf_report import STFReportSeverity, STFReport
from ....utils.component_utils import get_components_from_object
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister
from ....utils.id_utils import ensure_stf_id
from ....utils.buffer_utils import serialize_float


_stf_type = "stf.animation"


class STF_Animation(bpy.types.PropertyGroup):
	exclude: bpy.props.BoolProperty(name="Exclude from STF export", default=False) # type: ignore
	bake: bpy.props.BoolProperty(name="Bake Animation on Export", default=True) # type: ignore
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

	blender_animation.use_cyclic = False if json_resource.get("loop", "none") == "none" else True
	if("range" in json_resource):
		blender_animation.use_frame_range = True
		blender_animation.frame_start = json_resource["range"][0]
		blender_animation.frame_end = json_resource["range"][1]

	blender_animation.stf_animation.bake = json_resource.get("bake_on_export", True)

	# All of this is a mess

	layer = blender_animation.layers.new("stf_layer")
	strip: bpy.types.ActionKeyframeStrip = layer.strips.new(type="KEYFRAME")

	for track in json_resource.get("tracks", []):
		target_ret = context.resolve_stf_property_path(track.get("target", []))
		if(target_ret):
			target_object, application_object_property_index, slot_type, fcurve_target, index_conversion, conversion_func = target_ret
			if(not index_conversion):
				index_conversion = []
				for track_index in range(len(track.get("subtracks", []))):
					index_conversion.append(track_index)

			selected_slot_link = None
			for slot_link in blender_animation.slot_links:
				if(slot_link.target == target_object and slot_link.datablock_index == application_object_property_index):
					for slot in blender_animation.slots:
						if(slot.handle == slot_link.slot_handle and slot.target_id_type == slot_type):
							selected_slot_link = slot_link
							break
				if(selected_slot_link):
					break

			selected_channelbag = None
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
					break

			# Yay we can finally deal with curves
			__parse_subtracks(track, selected_channelbag, fcurve_target, index_conversion, conversion_func)

	return blender_animation

"""
def __parse_subtracks(track: dict, selected_channelbag: bpy.types.ActionChannelbag, fcurve_target: any, index_conversion: list[int], conversion_func: Callable[[list[float]], list[float]] = None):
	for subtrack_index, subtrack in enumerate(track.get("subtracks", [])):
		fcurve: bpy.types.FCurve = selected_channelbag.fcurves.new(fcurve_target, index=index_conversion[subtrack_index])
		for stf_keyframe in subtrack.get("keyframes", []):
			# Only import full unbaked keyframes
			is_source_keyframe = stf_keyframe[0]
			if(is_source_keyframe):
				timepoint = stf_keyframe[1]
				value = stf_keyframe[2]
				interpolation_type = stf_keyframe[3]
				if(interpolation_type == "bezier"):
					keyframe = fcurve.keyframe_points.insert(timepoint, value if not conversion_func else conversion_func(subtrack_index, value))
					keyframe.interpolation = "BEZIER"
					keyframe.handle_right_type = __handle_type_to_blender[stf_keyframe[4]]
					keyframe.handle_right.x = keyframe.co.x + stf_keyframe[5][0]
					keyframe.handle_right.y = (value + stf_keyframe[5][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[5][1])
					
					if(len(stf_keyframe) > 6):
						keyframe.handle_left_type = __handle_type_to_blender[stf_keyframe[4]]
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[6][0]
						keyframe.handle_left.y = (value + stf_keyframe[6][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[6][1])
				elif(interpolation_type == "constant"):
					keyframe = fcurve.keyframe_points.insert(timepoint, value if not conversion_func else conversion_func(subtrack_index, value))
					keyframe.interpolation = "CONSTANT"
					if(len(stf_keyframe) > 4):
						keyframe.handle_left_type = "ALIGNED"
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[4][0]
						keyframe.handle_left.y = (value + stf_keyframe[4][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[4][1])
				elif(interpolation_type == "linear"):
					keyframe = fcurve.keyframe_points.insert(timepoint, value if not conversion_func else conversion_func(subtrack_index, value))
					keyframe.interpolation = "LINEAR"
					if(len(stf_keyframe) > 4):
						keyframe.handle_left_type = "ALIGNED"
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[4][0]
						keyframe.handle_left.y = (value + stf_keyframe[4][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[4][1])
				# todo else warn about unsupported keyframe type
			# else keyframe is baked and can be ignored
		fcurve.keyframe_points.handles_recalc()
"""

# todo handle subtrack values in one go
def __parse_subtracks(track: dict, selected_channelbag: bpy.types.ActionChannelbag, fcurve_target: any, index_conversion: list[int], conversion_func: Callable[[list[float]], list[float]] = None):
	subtracks = track.get("subtracks", [])
	if(len(subtracks) == 0): return

	num_frames = -1

	fcurves: list[bpy.types.FCurve] = [None] * len(subtracks)
	for subtrack_index, subtrack in enumerate(subtracks):
		if(subtrack):
			fcurves[subtrack_index] = selected_channelbag.fcurves.new(fcurve_target, index=index_conversion[subtrack_index])
			num_frames = len(subtrack["keyframes"]) if len(subtrack["keyframes"]) > num_frames else num_frames
	
	if(num_frames <= 0): return

	for keyframe_index in range(num_frames):
		value_convert: list[float] = [None] * len(index_conversion)
		left_tangent_convert: list[float] = [0] * len(index_conversion)
		right_tangent_convert: list[float] = [0] * len(index_conversion)

		for subtrack_index, subtrack in enumerate(subtracks):
			if(not subtrack): continue

			stf_keyframe = subtrack["keyframes"][keyframe_index]

			value_convert[subtrack_index] = stf_keyframe[2]
			interpolation_type = stf_keyframe[3]
			if(interpolation_type == "bezier"):
				right_tangent_convert[subtrack_index] = stf_keyframe[5][1]
				if(len(stf_keyframe) > 6):
					left_tangent_convert[subtrack_index] = stf_keyframe[6][1]
			elif(interpolation_type == "constant" or interpolation_type == "linear"):
				if(len(stf_keyframe) > 4):
					left_tangent_convert[subtrack_index] = stf_keyframe[4][1]

		for i in range(len(index_conversion)):
			left_tangent_convert[i] += value_convert[i]
			right_tangent_convert[i] += value_convert[i]

		if(conversion_func):
			value_convert = conversion_func(value_convert)
			left_tangent_convert = conversion_func(left_tangent_convert)
			right_tangent_convert = conversion_func(right_tangent_convert)

		# todo create keyframe
		for subtrack_index, subtrack in enumerate(subtracks):
			if(not subtrack): continue
			
			stf_keyframe = subtrack["keyframes"][keyframe_index]
			if(not stf_keyframe[0]): continue # Not source of truth, ignore
			
			keyframe = fcurve.keyframe_points.insert(stf_keyframe[1], value_convert[subtrack_index[index_conversion]])
			# todo

	for fcurve in fcurves:
		if(fcurve):
			fcurve.keyframe_points.handles_recalc()

	# todo remove below
	"""for subtrack_index, subtrack in subtrack:
		fcurve: bpy.types.FCurve = selected_channelbag.fcurves.new(fcurve_target, index=index_conversion[subtrack_index])
		for stf_keyframe in subtrack.get("keyframes", []):
			# Only import full unbaked keyframes
			is_source_keyframe = stf_keyframe[0]
			if(is_source_keyframe):
				timepoint = stf_keyframe[1]
				value = stf_keyframe[2]
				interpolation_type = stf_keyframe[3]
				if(interpolation_type == "bezier"):
					keyframe = fcurve.keyframe_points.insert(timepoint, value if not conversion_func else conversion_func(subtrack_index, value))
					keyframe.interpolation = "BEZIER"
					keyframe.handle_right_type = __handle_type_to_blender[stf_keyframe[4]]
					keyframe.handle_right.x = keyframe.co.x + stf_keyframe[5][0]
					keyframe.handle_right.y = (value + stf_keyframe[5][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[5][1])
					
					if(len(stf_keyframe) > 6):
						keyframe.handle_left_type = __handle_type_to_blender[stf_keyframe[4]]
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[6][0]
						keyframe.handle_left.y = (value + stf_keyframe[6][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[6][1])
				elif(interpolation_type == "constant"):
					keyframe = fcurve.keyframe_points.insert(timepoint, value if not conversion_func else conversion_func(subtrack_index, value))
					keyframe.interpolation = "CONSTANT"
					if(len(stf_keyframe) > 4):
						keyframe.handle_left_type = "ALIGNED"
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[4][0]
						keyframe.handle_left.y = (value + stf_keyframe[4][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[4][1])
				elif(interpolation_type == "linear"):
					keyframe = fcurve.keyframe_points.insert(timepoint, value if not conversion_func else conversion_func(subtrack_index, value))
					keyframe.interpolation = "LINEAR"
					if(len(stf_keyframe) > 4):
						keyframe.handle_left_type = "ALIGNED"
						keyframe.handle_left.x = keyframe.co.x + stf_keyframe[4][0]
						keyframe.handle_left.y = (value + stf_keyframe[4][1]) if not conversion_func else conversion_func(subtrack_index, value + stf_keyframe[4][1])
				# todo else warn about unsupported keyframe type
			# else keyframe is baked and can be ignored
		fcurve.keyframe_points.handles_recalc()"""


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
		"loop": "cycle" if blender_animation.use_cyclic else "none", # todo create ui for this setting
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
							if(property_translation):
								target, conversion_func, index_conversion = property_translation
								if(not index_conversion):
									index_conversion = []
									for _, fcurve in fcurves.items():
										if(fcurve):
											index_conversion.append(fcurve.array_index)

								sub_tracks = __serialize_subtracks(context, blender_animation, fcurves, ret["range"], index_conversion, conversion_func)

								stf_tracks.append({
									"target": target,
									"subtracks": sub_tracks
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


def __serialize_subtracks(context: STF_ExportContext, blender_animation: bpy.types.Action, fcurves: dict[int, bpy.types.FCurve], animation_range: list[float], index_conversion: list[int], conversion_func: Callable[[list[float]], list[float]] = None) -> list:
	real_timepoints_set: set[float] = set()
	# for each subtrack (i.e. the x,y,z components of a location), determine at wich times have a keyframe at any of these subtracks
	for _, fcurve in fcurves.items():
		for keyframe in fcurve.keyframe_points:
			real_timepoints_set.add(keyframe.co.x)
	real_timepoints = list(real_timepoints_set)
	real_timepoints.sort()

	# Set empty track objects
	ret: list[dict | None] = [None] * len(index_conversion)
	for _, fcurve in fcurves.items():
		ret[index_conversion[fcurve.array_index]] = {"keyframes": []}

	# Bake values if desired
	if(blender_animation.stf_animation.bake):
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

				value = value_convert[index_conversion[fcurve.array_index]]

				stf_keyframe = [
					True, # is source of truth, false because it's baked
					keyframe.co.x, # frame number
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
						__handle_type_to_stf.get(keyframe.handle_right_type, "split"), # tangent type
						[(keyframe.handle_right.x - keyframe.co.x) / right_tangent_factor, (value_convert[index_conversion[fcurve.array_index]] - right_tangent_convert[index_conversion[fcurve.array_index]]) / right_tangent_factor], # right tangent values relative to keyframe
					]
					if(left_tangent):
						stf_keyframe + left_tangent

				elif(keyframe.interpolation == "CONSTANT"):
					stf_keyframe.append("constant")
					# todo
					if(left_tangent):
						stf_keyframe + left_tangent

				elif(keyframe.interpolation == "LINEAR"):
					stf_keyframe.append("linear")
					# todo
					if(left_tangent):
						stf_keyframe + left_tangent
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

	return ret


__handle_type_to_stf = {
	"FREE": "split",
	"ALIGNED": "aligned",
	"AUTO_CLAMPED": "auto",
	"AUTOMATIC": "auto",
}
__handle_type_to_blender = {
	"split": "FREE",
	"aligned": "ALIGNED",
	"auto": "AUTO_CLAMPED"
}


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
