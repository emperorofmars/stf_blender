from typing import Callable
import bpy

from .stf_animation_common import *
from ....base.stf_task_steps import STF_TaskSteps
from ....importer.stf_import_context import STF_ImportContext
from ....base.stf_report import STFReportSeverity, STFReport


_stf_type = stf_animation_type


def stf_animation_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	if(not hasattr(bpy.types.Action, "slot_link")):
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

	# All of this is a mess

	layer = blender_animation.layers.new("stf_layer")
	strip: bpy.types.ActionKeyframeStrip = layer.strips.new(type="KEYFRAME")

	for track in json_resource.get("tracks", []):
		target_ret = context.resolve_stf_property_path(track.get("target", []))
		if(not target_ret):
			continue

		index_conversion = target_ret.index_conversion

		if(not index_conversion):
			index_conversion = []
			for track_index in range(len(track.get("subtracks", []))):
				index_conversion.append(track_index)

		selected_slot_link = None
		for slot_link in blender_animation.slot_link.links:
			if(slot_link.target == target_ret.slot_link_target and slot_link.datablock_index == target_ret.slot_link_property_index):
				for slot in blender_animation.slots:
					if(slot.handle == slot_link.slot_handle and slot.target_id_type == target_ret.slot_type):
						selected_slot_link = slot_link
						break
			if(selected_slot_link):
				break

		selected_channelbag = None
		if(not selected_slot_link):
			blender_slot = blender_animation.slots.new(target_ret.slot_type, target_ret.slot_link_target.name + " - " + target_ret.slot_type)
			selected_slot_link = blender_animation.slot_link.links.add()
			selected_slot_link.slot_handle = blender_slot.handle
			selected_slot_link.target = target_ret.slot_link_target
			selected_slot_link.datablock_index = target_ret.slot_link_property_index
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
		__parse_subtracks(track, selected_channelbag, target_ret.blender_path, index_conversion, target_ret.convert_func)
	
	def _handle_reset_animation():
		if("is_reset_animation" in json_resource and json_resource["is_reset_animation"] == True):
			blender_animation.slot_link.is_reset_animation = True
		elif("reset_animation" in json_resource and json_resource["reset_animation"]):
			if(reset_animation := context.import_resource(json_resource["reset_animation"], context_object, "data")):
				blender_animation.slot_link.reset_animation = reset_animation
	context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle_reset_animation)

	blender_animation.use_fake_user = True

	return blender_animation


def __parse_subtracks(track: dict, selected_channelbag: bpy.types.ActionChannelbag, fcurve_target: any, index_conversion: list[int], conversion_func: Callable[[list[float]], list[float]] = None):
	subtracks = track.get("subtracks", [])
	timepoints = track.get("timepoints", [])
	if(len(subtracks) == 0 or len(timepoints) == 0): return

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
			timepoint = timepoints[keyframe_index]

			has_left_tangent = False
			left_tangent_index = 0

			value_convert[subtrack_index] = stf_keyframe[1]
			interpolation_type = stf_keyframe[2]
			if(interpolation_type == "bezier"):
				right_tangent_convert[subtrack_index] = stf_keyframe[4][1]
				if(len(stf_keyframe) > 5):
					has_left_tangent = True
					left_tangent_index = 5
					left_tangent_convert[subtrack_index] = stf_keyframe[5][1]
			elif(interpolation_type in ["constant", "linear", "quadratic", "cubic"]):
				if(len(stf_keyframe) > 3):
					has_left_tangent = True
					left_tangent_index = 4
					left_tangent_convert[subtrack_index] = stf_keyframe[3][1]

		for i in range(len(index_conversion)):
			left_tangent_convert[i] += value_convert[i]
			right_tangent_convert[i] += value_convert[i]

		if(conversion_func):
			value_convert = conversion_func(value_convert)
			left_tangent_convert = conversion_func(left_tangent_convert)
			right_tangent_convert = conversion_func(right_tangent_convert)

		for subtrack_index, subtrack in enumerate(subtracks):
			if(not subtrack): continue
			
			stf_keyframe = subtrack["keyframes"][keyframe_index]
			if(not stf_keyframe[0]): continue # Not source of truth, ignore
			
			keyframe = fcurves[subtrack_index].keyframe_points.insert(timepoint, value_convert[index_conversion[subtrack_index]])

			interpolation_type = stf_keyframe[2]
			if(interpolation_type == "bezier"):
				keyframe.interpolation = "BEZIER"
				keyframe.handle_right_type = handle_type_to_blender[stf_keyframe[3]]
				keyframe.handle_right.x = keyframe.co.x + stf_keyframe[4][0]
				keyframe.handle_right.y = right_tangent_convert[index_conversion[subtrack_index]]
			elif(interpolation_type == "constant"):
				keyframe.interpolation = "CONSTANT"
			elif(interpolation_type == "linear"):
				keyframe.interpolation = "LINEAR"
			elif(interpolation_type == "quadratic"):
				keyframe.interpolation = "QUAD"
			elif(interpolation_type == "cubic"):
				keyframe.interpolation = "CUBIC"
			# todo else warn about unsupported keyframe type

			if(has_left_tangent and len(stf_keyframe) > left_tangent_index):
				#keyframe.handle_left_type = "FREE"
				keyframe.handle_left.x = keyframe.co.x + stf_keyframe[left_tangent_index][0]
				keyframe.handle_left.y =  left_tangent_convert[index_conversion[subtrack_index]]

	for fcurve in fcurves:
		if(fcurve):
			fcurve.keyframe_points.handles_recalc()
