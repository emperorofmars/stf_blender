import bpy
import math
from typing import Any
from collections.abc import Sequence

from ...common import STF_ExportContext, STF_ImportContext, STF_Category, STFReport
from ...common.resource.component import STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref
from ...common.resource.component.component_utils import add_component, export_component_base, import_component_base


_stf_type = "stfexp.armature.humanoid"
_blender_property_name = "stfexp_armature_humanoid"


# ends_with, starts_with
_mappings_left_side = (("left", "_l", ".l", "-l"), ("left", ))
_mappings_right_side = (("right", "_r", ".r", "-r"), ("right", ))

# (humanoid_name, display_name, matching_conditions, side (None | "l" | "r"), muscle_rotation_limits(False | [[p_min, p_max],[s_min, s_max],[t_min, t_max]]))
_humanoid_bones: Sequence[tuple[str, str, Sequence[Sequence[Sequence[str]]], str | None, Sequence[Sequence[float] | None] | None]] = (
	("hip", "Hip", ((("hip", "hips"),),), None, False),
	("spine", "Spine", ((("spine",),),), None, [[-40, 40],[-40, 40],[-40, 40]]),
	("chest", "Chest", ((("chest",),),), None, [[-40, 40],[-40, 40],[-40, 40]]),
	("upper_chest", "Upper Chest", ((("upper", "up"), ("chest",)),), None, False),
	("neck", "Neck", ((("neck",),),), None, [[-40, 40],[-40, 40],[-40, 40]]),
	("head", "Head", ((("head",),),), None, [[-40, 40],[-40, 40],[-40, 40]]),
	("jaw", "Jaw", ((("jaw",),),), None, False),
	("eye.l", "Left Eye", ((("eye",),),), "l", [[-10, 15],[-20, 20],False]),
	("eye.r", "Right Eye", ((("eye",),),), "r", [[-10, 15],[-20, 20],False]),

	("shoulder.l", "Left Shoulder", [[["shoulder", "collar"]]], "l", [[-15, 30],[-15, 15],False]),
	("upper_arm.l", "Left Upper Arm", [[["arm"]], [["upper", "up"], ["arm"]]], "l", [[-60, 100],[-100, 100],[-90, 90]]),
	("lower_arm.l", "Left Lower Arm", [[["elbow"]], [["lower", "low", "fore"], ["arm"]]], "l", [[-80, 80],False,[-90, 90]]),
	("wrist.l", "Left Wrist", [[["hand", "wrist"]]], "l", [[-80, 80],[-40, 40],False]),

	("thumb_1.l", "Left Thumb Proximal", [[["finger", "f", ""], ["thumb"], ["1", "proximal"]]], "l", [[-20, 20],[-25, 25],False]),
	("thumb_2.l", "Left Thumb Intermediate", [[["finger", "f", ""], ["thumb"], ["2", "intermediate"]]], "l", [[-40, 35],False,False]),
	("thumb_3.l", "Left Thumb Distal", [[["finger", "f", ""], ["thumb"], ["3", "distal"]]], "l", [[-40, 35],False,False]),
	("index_1.l", "Left Index Proximal", [[["finger", "f", ""], ["index"], ["1", "proximal"]]], "l", [[-50, 50],[-20,20],False]),
	("index_2.l", "Left Index Intermediate", [[["finger", "f", ""], ["index"], ["2", "intermediate"]]], "l", [[-45, 45],False,False]),
	("index_3.l", "Left Index Distal", [[["finger", "f", ""], ["index"], ["3", "distal"]]], "l", [[-45, 45],False,False]),
	("middle_1.l", "Left Middle Proximal", [[["finger", "f", ""], ["middle"], ["1", "proximal"]]], "l", [[-50, 50],[-7.5,7.5],False]),
	("middle_2.l", "Left Middle Intermediate", [[["finger", "f", ""], ["middle"], ["2", "intermediate"]]], "l", [[-45, 45],False,False]),
	("middle_3.l", "Left Middle Distal", [[["finger", "f", ""], ["middle"], ["3", "distal"]]], "l", [[-45, 45],False,False]),
	("ring_1.l", "Left Ring Proximal", [[["finger", "f", ""], ["ring"], ["1", "proximal"]]], "l", [[-50, 50],[-7.5,7.5],False]),
	("ring_2.l", "Left Ring Intermediate", [[["finger", "f", ""], ["ring"], ["2", "intermediate"]]], "l", [[-45, 45],False,False]),
	("ring_3.l", "Left Ring Distal", [[["finger", "f", ""], ["ring"], ["3", "distal"]]], "l", [[-45, 45],False,False]),
	("little_1.l", "Left Little Proximal", [[["finger", "f", ""], ["little", "pinkie", "pinky"], ["1", "proximal"]]], "l", [[-50, 50],[-20,20],False]),
	("little_2.l", "Left Little Intermediate", [[["finger", "f", ""], ["little", "pinkie", "pinky"], ["2", "intermediate"]]], "l", [[-45, 45],False,False]),
	("little_3.l", "Left Little Distal", [[["finger", "f", ""], ["little", "pinkie", "pinky"], ["3", "distal"]]], "l", [[-45, 45],False,False]),

	("shoulder.r", "Right Shoulder", [[["shoulder", "collar"]]], "r", [[-15, 30],[-15, 15],False]),
	("upper_arm.r", "Right Upper Arm", [[["arm"]], [["upper", "up"], ["arm"]]], "r", [[-60, 100],[-100, 100],[-90, 90]]),
	("lower_arm.r", "Right Lower Arm", [[["elbow"]], [["lower", "low", "fore"], ["arm"]]], "r", [[-80, 80],False,[-90, 90]]),
	("wrist.r", "Right Wrist", [[["hand", "wrist"]]], "r", [[-80, 80],[-40, 40],False]),

	("thumb_1.r", "Right Thumb Proximal", [[["finger", "f", ""], ["thumb"], ["1", "proximal"]]], "r", [[-20, 20],[-25, 25],False]),
	("thumb_2.r", "Right Thumb Intermediate", [[["finger", "f", ""], ["thumb"], ["2", "intermediate"]]], "r", [[-40, 35],False,False]),
	("thumb_3.r", "Right Thumb Distal", [[["finger", "f", ""], ["thumb"], ["3", "distal"]]], "r", [[-40, 35],False,False]),
	("index_1.r", "Right Index Proximal", [[["finger", "f", ""], ["index"], ["1", "proximal"]]], "r", [[-50, 50],[-20,20],False]),
	("index_2.r", "Right Index Intermediate", [[["finger", "f", ""], ["index"], ["2", "intermediate"]]], "r", [[-45, 45],False,False]),
	("index_3.r", "Right Index Distal", [[["finger", "f", ""], ["index"], ["3", "distal"]]], "r", [[-45, 45],False,False]),
	("middle_1.r", "Right Middle Proximal", [[["finger", "f", ""], ["middle"], ["1", "proximal"]]], "r", [[-50, 50],[-7.5,7.5],False]),
	("middle_2.r", "Right Middle Intermediate", [[["finger", "f", ""], ["middle"], ["2", "intermediate"]]], "r", [[-45, 45],False,False]),
	("middle_3.r", "Right Middle Distal", [[["finger", "f", ""], ["middle"], ["3", "distal"]]], "r", [[-45, 45],False,False]),
	("ring_1.r", "Right Ring Proximal", [[["finger", "f", ""], ["ring"], ["1", "proximal"]]], "r", [[-50, 50],[-7.5,7.5],False]),
	("ring_2.r", "Right Ring Intermediate", [[["finger", "f", ""], ["ring"], ["2", "intermediate"]]], "r", [[-45, 45],False,False]),
	("ring_3.r", "Right Ring Distal", [[["finger", "f", ""], ["ring"], ["3", "distal"]]], "r", [[-45, 45],False,False]),
	("little_1.r", "Right Little Proximal", [[["finger", "f", ""], ["little", "pinkie", "pinky"], ["1", "proximal"]]], "r", [[-50, 50],[-20,20],False]),
	("little_2.r", "Right Little Intermediate", [[["finger", "f", ""], ["little", "pinkie", "pinky"], ["2", "intermediate"]]], "r", [[-45, 45],False,False]),
	("little_3.r", "Right Little Distal", [[["finger", "f", ""], ["little", "pinkie", "pinky"], ["3", "distal"]]], "r", [[-45, 45],False,False]),

	("upper_leg.l", "Left Upper Leg", [[["leg"], ["upper", "up"]], [["thigh", "leg"]]], "l", [[-90, 90],[-60, 60],[-60, 60]]),
	("lower_leg.l", "Left Lower Leg", [[["leg"], ["lower", "low"]], [["shin", "knee"]]], "l", [[-80, 80],False,[-90, 90]]),
	("foot.l", "Left Foot", [[["foot", "feet", "ankle"]]], "l", [[-50, 50],False,[-30, 30]]),
	("toes.l", "Left Toes", [[["toes", "toe"]]], "l", False),

	("upper_leg.r", "Right Upper Leg", [[["leg"], ["upper", "up"]], [["thigh", "leg"]]], "r", [[-90, 90],[-60, 60],[-60, 60]]),
	("lower_leg.r", "Right Lower Leg", [[["leg"], ["lower", "low"]], [["shin", "knee"]]], "r", [[-80, 80],False,[-90, 90]]),
	("foot.r", "Right Foot", [[["foot", "feet", "ankle"]]], "r", [[-50, 50],False,[-30, 30]]),
	("toes.r", "Right Toes", [[["toes", "toe"]]], "r", False),
)

def _get_display_name(humanoid_name: str) -> str:
	for bone in _humanoid_bones:
		if(bone[0] == humanoid_name):
			return bone[1]
	return None


class HumanoidBone(bpy.types.PropertyGroup):
	bone: bpy.props.StringProperty(name="Bone", description="Bone on the Armature that maps onto the humanoid name", options=set()) # type: ignore

	set_rotation_limits: bpy.props.BoolProperty(name="Set Rotation Limits", default=False, options=set()) # type: ignore

	p_min: bpy.props.FloatProperty(name="Primary Min", subtype="ANGLE", default=math.radians(-60), soft_min=math.radians(-180), soft_max=math.radians(0), precision=2, options=set()) # type: ignore
	p_center: bpy.props.FloatProperty(name="Primary Center", subtype="ANGLE", default=0, soft_min=math.radians(-180), soft_max=math.radians(180), precision=2, options=set()) # type: ignore
	p_max: bpy.props.FloatProperty(name="Primary Max", subtype="ANGLE", default=math.radians(60), soft_min=math.radians(0), soft_max=math.radians(180), precision=2, options=set()) # type: ignore
	s_min: bpy.props.FloatProperty(name="Secondary Min", subtype="ANGLE", default=math.radians(-60), soft_min=math.radians(-180), soft_max=math.radians(0), precision=2, options=set()) # type: ignore
	s_center: bpy.props.FloatProperty(name="Primary Center", subtype="ANGLE", default=0, soft_min=math.radians(-180), soft_max=math.radians(180), precision=2, options=set()) # type: ignore
	s_max: bpy.props.FloatProperty(name="Secondary Max", subtype="ANGLE", default=math.radians(60), soft_min=math.radians(0), soft_max=math.radians(180), precision=2, options=set()) # type: ignore
	t_min: bpy.props.FloatProperty(name="Twist Min", subtype="ANGLE", default=math.radians(-90), soft_min=math.radians(-180), soft_max=math.radians(0), precision=2, options=set()) # type: ignore
	t_center: bpy.props.FloatProperty(name="Primary Center", subtype="ANGLE", default=0, soft_min=math.radians(-180), soft_max=math.radians(180), precision=2, options=set()) # type: ignore
	t_max: bpy.props.FloatProperty(name="Twist Max", subtype="ANGLE", default=math.radians(90), soft_min=math.radians(0), soft_max=math.radians(180), precision=2, options=set()) # type: ignore


class HumanoidSettings(bpy.types.PropertyGroup):
	arm_stretch: bpy.props.FloatProperty(name="Arm Stretch", default=0.053, soft_min=0, soft_max=1, precision=3, options=set()) # type: ignore
	upper_arm_twist: bpy.props.FloatProperty(name="Upper Arm Twist", default=0.5, soft_min=0, soft_max=1, precision=2, options=set()) # type: ignore
	lower_arm_twist: bpy.props.FloatProperty(name="Lower Arm Twist", default=0.5, soft_min=0, soft_max=1, precision=2, options=set()) # type: ignore
	leg_stretch: bpy.props.FloatProperty(name="Leg Stretch", default=0.05, soft_min=0, soft_max=1, precision=3, options=set()) # type: ignore
	upper_leg_twist: bpy.props.FloatProperty(name="Upper Leg Twist", default=0.5, soft_min=0, soft_max=1, precision=2, options=set()) # type: ignore
	lower_leg_twist: bpy.props.FloatProperty(name="Lower Leg Twist", default=0.5, soft_min=0, soft_max=1, precision=2, options=set()) # type: ignore

	feet_spacing: bpy.props.FloatProperty(name="Feet Spacing", default=0, soft_min=0, soft_max=1, precision=2, options=set()) # type: ignore
	use_translation: bpy.props.BoolProperty(name="Feet Spacing", default=False, options=set()) # type: ignore


class STFEXP_Armature_Humanoid(STF_ComponentResourceBase):
	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti", options=set()) # type: ignore
	no_jaw: bpy.props.BoolProperty(name="Ignore Jaw Mapping", default=False, options=set()) # type: ignore

	bone_mappings: bpy.props.CollectionProperty(type=HumanoidBone, name="Humanoid Mappings", options=set()) # type: ignore
	active_bone_mapping: bpy.props.IntProperty() # type: ignore

	settings: bpy.props.PointerProperty(type=HumanoidSettings, name="Humanoid Settings", options=set()) # type: ignore


def _setup_humanoid_collection(component: STFEXP_Armature_Humanoid):
	component.bone_mappings.clear()
	for bone in _humanoid_bones:
		mapping: HumanoidBone = component.bone_mappings.add()
		mapping.name = bone[0]
		if(bone[4] and len(bone[4]) == 3):
			if(bone[4][0]):
				mapping.p_min = math.radians(bone[4][0][0])
				mapping.p_max = math.radians(bone[4][0][1])
			if(bone[4][1]):
				mapping.s_min = math.radians(bone[4][1][0])
				mapping.s_max = math.radians(bone[4][1][1])
			if(bone[4][2]):
				mapping.t_min = math.radians(bone[4][2][0])
				mapping.t_max = math.radians(bone[4][2][1])

def _map_humanoid_bones(component: STFEXP_Armature_Humanoid, armature: bpy.types.Armature):
	if(len(component.bone_mappings) != len(_humanoid_bones)):
		_setup_humanoid_collection(component)

	for bone_mapping in _humanoid_bones:
		mapping_conditions: tuple = bone_mapping[2]
		side: str | None = bone_mapping[3]
		candidate = None
		candidate_confidence = -1
		for bone in armature.bones:
			for outer_or_condition in mapping_conditions:
				and_success = True
				and_len = 0
				for and_condition in outer_or_condition:
					or_success = False
					or_len = 0
					for or_condition in and_condition:
						if(or_condition in bone.name.lower()):
							or_success = True
							or_len = max(or_len, len(or_condition))
					if(or_success):
						and_len += or_len
					else:
						and_success = False
						break
				if(not and_success):
					continue
				confidence = and_len / max(len(bone.name), 1)
				if(confidence <= candidate_confidence):
					continue

				if(side == "r"):
					for side_mapping in _mappings_right_side[0]:
						if(bone.name.lower().endswith(side_mapping)):
							break
					else:
						for side_mapping in _mappings_right_side[1]:
							if(bone.name.lower().startswith(side_mapping)):
								break
						else:
							continue
				elif(side == "l"):
					for side_mapping in _mappings_left_side[0]:
						if(bone.name.lower().endswith(side_mapping)):
							break
					else:
						for side_mapping in _mappings_left_side[1]:
							if(bone.name.lower().startswith(side_mapping)):
								break
						else:
							continue
				candidate = bone.name
				candidate_confidence = confidence
		if(candidate):
			component.bone_mappings[bone_mapping[0]].bone = candidate
		else:
			component.bone_mappings[bone_mapping[0]].bone = ""


class ResetHumanoidCollectionOperator(bpy.types.Operator):
	"""Setup empty humanoid mappings. Will overwrite any existing values"""
	bl_idname = "stf.stfexp_armature_humanoid_reset_collection"
	bl_label = "Reset"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "armature") and context.armature is not None

	def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context: bpy.types.Context):
		# let component
		for component in context.armature.stfexp_armature_humanoid:
			component.stf_id == self.component_id
			break
		else:
			self.report({"ERROR"}, "Failed")
			return {"CANCELLED"}
		_setup_humanoid_collection(component)
		return {"FINISHED"}

class MapHumanoidCollectionOperator(bpy.types.Operator):
	"""Setup humanoid mappings. Will overwrite any existing bone mappings"""
	bl_idname = "stf.stfexp_armature_humanoid_map_collection"
	bl_label = "Map"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	@classmethod
	def poll(cls, context: bpy.types.Context):
		return hasattr(context, "armature") and context.armature is not None

	def invoke(self, context: bpy.types.Context, event: bpy.types.Event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context: bpy.types.Context):
		# let component
		for component in context.armature.stfexp_armature_humanoid:
			component.stf_id == self.component_id
			break
		else:
			self.report({"ERROR"}, "Failed")
			return {"CANCELLED"}
		_map_humanoid_bones(component, context.armature)
		return {"FINISHED"}


class STFEXP_HumanoidMappingsList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stfexp_humanoid_mappings_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data: STFEXP_Armature_Humanoid, item: HumanoidBone, icon, active_data, active_propname, index):
		for candidate_mapping in data.bone_mappings:
			if(candidate_mapping != item and candidate_mapping.bone == item.bone):
				layout.alert = True
				break

		layout.label(text=_get_display_name(item.name), icon="NONE" if item.bone else "ERROR")
		layout.label(text=item.bone if item.bone else "Not Mapped!", icon="BONE_DATA" if item.bone else "ERROR")

def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: bpy.types.Armature, component: STFEXP_Armature_Humanoid):
	layout.use_property_split = True

	col = layout.column(align=True)
	col.prop(component.settings, "arm_stretch")
	col.prop(component.settings, "upper_arm_twist")
	col.prop(component.settings, "lower_arm_twist")
	col.prop(component.settings, "leg_stretch")
	col.prop(component.settings, "upper_leg_twist")
	col.prop(component.settings, "lower_leg_twist")
	col.prop(component.settings, "feet_spacing")
	col.prop(component.settings, "use_translation")

	layout.separator(factor=2, type="LINE")

	layout.prop(component, "locomotion_type")
	layout.prop(component, "no_jaw")

	layout.separator(factor=2, type="LINE")

	row = layout.row()
	row.operator(ResetHumanoidCollectionOperator.bl_idname, icon="WARNING_LARGE")
	row.operator(MapHumanoidCollectionOperator.bl_idname, icon="LOOP_FORWARDS")

	mapped = 0
	for mapping in component.bone_mappings:
		if(mapping.bone and mapping.bone in context_object.bones):
			mapped += 1
	if(mapped < len(_humanoid_bones)):
		layout.label(text=f"Mapped {mapped} of {len(_humanoid_bones)} Bones.", icon="WARNING_LARGE")

	layout.template_list(STFEXP_HumanoidMappingsList.bl_idname, "", component, "bone_mappings", component, "active_bone_mapping")
	if(len(component.bone_mappings) > component.active_bone_mapping):
		mapping = component.bone_mappings[component.active_bone_mapping]
		for mapping_definition in _humanoid_bones:
			if(mapping.name == mapping_definition[0]):
				break
		else:
			return

		col = layout.column()
		for candidate_mapping in component.bone_mappings:
			if(candidate_mapping != mapping and candidate_mapping.bone == mapping.bone):
				col.alert = True
				col.label(text="Duplicate Bone Mapping! Bone '" + mapping.bone + "' is also mapped in " + _get_display_name(candidate_mapping.name), icon="ERROR")
				break
		col.prop_search(mapping, "bone", context_object, "bones", text="Mapped Bone")

		if(mapping_definition[4] and len(mapping_definition[4]) == 3):
			layout.prop(mapping, "set_rotation_limits")
			if(mapping.set_rotation_limits):
				col = layout.column(align=True)
				if(mapping_definition[4][0]):
					row = col.row(align=True)
					row.use_property_split = False
					row.label(text="Primary Axis")
					row.prop(mapping, "p_min", text="Min")
					row.prop(mapping, "p_center", text="Center")
					row.prop(mapping, "p_max", text="Max")
				if(mapping_definition[4][1]):
					row = col.row(align=True)
					row.use_property_split = False
					row.label(text="Secondary Axis")
					row.prop(mapping, "s_min", text="Min")
					row.prop(mapping, "s_center", text="Center")
					row.prop(mapping, "s_max", text="Max")
				if(mapping_definition[4][2]):
					row = col.row(align=True)
					row.use_property_split = False
					row.label(text="Twist")
					row.prop(mapping, "t_min", text="Min")
					row.prop(mapping, "t_center", text="Center")
					row.prop(mapping, "t_max", text="Max")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: Any) -> Any | STFReport:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	component: STFEXP_Armature_Humanoid = component
	import_component_base(context, component, json_resource, _blender_property_name, context_object)

	component.locomotion_type = json_resource.get("locomotion_type", "planti")
	component.no_jaw = json_resource.get("no_jaw", False)

	if("settings" in json_resource):
		component.settings.arm_stretch = json_resource["settings"]["arm_stretch"]
		component.settings.upper_arm_twist = json_resource["settings"]["upper_arm_twist"]
		component.settings.lower_arm_twist = json_resource["settings"]["lower_arm_twist"]
		component.settings.leg_stretch = json_resource["settings"]["leg_stretch"]
		component.settings.upper_leg_twist = json_resource["settings"]["upper_leg_twist"]
		component.settings.lower_leg_twist = json_resource["settings"]["lower_leg_twist"]
		component.settings.feet_spacing = json_resource["settings"]["feet_spacing"]
		component.settings.use_translation = json_resource["settings"]["use_translation"]

	if("mappings" in json_resource):
		_setup_humanoid_collection(component)
		for humanoid_name, json_mapping in json_resource["mappings"].items():
			for mapping_definition in _humanoid_bones:
				if(humanoid_name == mapping_definition[0]):
					break
			else:
				continue
			if("target" in json_mapping and humanoid_name in component.bone_mappings):
				if(target := context.get_imported_resource(json_mapping["target"])):
					component.bone_mappings[humanoid_name].bone = target.get_bone().name
					if("rotation_limits" in json_mapping):
						component.bone_mappings[humanoid_name].set_rotation_limits = True
						if("primary" in json_mapping["rotation_limits"] and len(json_mapping["rotation_limits"]["primary"]) == 3):
							component.bone_mappings[humanoid_name].p_min = json_mapping["rotation_limits"]["primary"][0]
							component.bone_mappings[humanoid_name].p_center = json_mapping["rotation_limits"]["primary"][1]
							component.bone_mappings[humanoid_name].p_max = json_mapping["rotation_limits"]["primary"][0]
						if("secondary" in json_mapping["rotation_limits"] and len(json_mapping["rotation_limits"]["secondary"]) == 3):
							component.bone_mappings[humanoid_name].s_min = json_mapping["rotation_limits"]["secondary"][0]
							component.bone_mappings[humanoid_name].s_center = json_mapping["rotation_limits"]["secondary"][1]
							component.bone_mappings[humanoid_name].s_max = json_mapping["rotation_limits"]["secondary"][0]
						if("twist" in json_mapping["rotation_limits"] and len(json_mapping["rotation_limits"]["twist"]) == 3):
							component.bone_mappings[humanoid_name].t_min = json_mapping["rotation_limits"]["twist"][0]
							component.bone_mappings[humanoid_name].t_center = json_mapping["rotation_limits"]["twist"][1]
							component.bone_mappings[humanoid_name].t_max = json_mapping["rotation_limits"]["twist"][0]

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Armature_Humanoid, context_object: Any) -> tuple[dict, str] | STFReport:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	ret["locomotion_type"] = component.locomotion_type
	ret["no_jaw"] = component.no_jaw

	ret["settings"] = {
		"arm_stretch": component.settings.arm_stretch,
		"upper_arm_twist": component.settings.upper_arm_twist,
		"lower_arm_twist": component.settings.lower_arm_twist,
		"leg_stretch": component.settings.leg_stretch,
		"upper_leg_twist": component.settings.upper_leg_twist,
		"lower_leg_twist": component.settings.lower_leg_twist,
		"feet_spacing": component.settings.feet_spacing,
		"use_translation": component.settings.use_translation,
	}

	mappings: dict[str, dict] = {}
	for mapping in component.bone_mappings:
		for mapping_definition in _humanoid_bones:
			if(mapping.name == mapping_definition[0]):
				break
		else:
			continue
		if(mapping.bone):
			json_mapping = { "target": context_object.bones[mapping.bone].stf_info.stf_id }
			if(mapping.set_rotation_limits and mapping_definition[4] and len(mapping_definition[4]) == 3):
				json_limits = {}
				if(mapping_definition[4][0]):
					json_limits["primary"] = [mapping.p_min, mapping.p_center, mapping.p_max]
				if(mapping_definition[4][1]):
					json_limits["secondary"] = [mapping.s_min, mapping.s_center, mapping.s_max]
				if(mapping_definition[4][2]):
					json_limits["twist"] = [mapping.t_min, mapping.t_center, mapping.t_max]
				json_mapping["rotation_limits"] = json_limits
			mappings[mapping.name] = json_mapping
	if(len(mappings) > 0):
		ret["mappings"] = mappings

	return ret, component.stf_id


class Handler_STFEXP_Armature_Humanoid(STF_Handler_Component):
	"""Declares that this Armature is humanoid. Must satisfy the requirements for the Unity/VRM humanoid rig"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["armature_humanoid"]
	understood_application_types = [STFEXP_Armature_Humanoid]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]
	draw_component_func = _draw_component

	pretty_name_template = "Humanoid Bone Mappings"


register_stf_handlers = [
	Handler_STFEXP_Armature_Humanoid
]


def register():
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Armature_Humanoid))

def unregister():
	if hasattr(bpy.types.Armature, _blender_property_name):
		delattr(bpy.types.Armature, _blender_property_name)
