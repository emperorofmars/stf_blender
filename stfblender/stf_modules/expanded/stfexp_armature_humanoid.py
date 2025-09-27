import bpy

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "stfexp.armature.humanoid"
_blender_property_name = "stfexp_armature_humanoid"


_mappings_left_side = ["left", "_l", ".l", "-l", " l"]
_mappings_right_side = ["right", "_r", ".r", "-r", " l"]

# (humanoid_name, display_name, matching_elements)
_humanoid_bones = [
	("hip", "Hip", [["hip", "hips"]]),
	("spine", "Spine", [["spine"]]),
	("chest", "Chest", [["chest"]]),
	("upper_chest", "Upper Chest", [["upper"], ["chest"]]),
	("neck", "Neck", [["neck"]]),
	("head", "Head", [["head"]]),
	("jaw", "Jaw", [["jaw"]]),
	("eye.l", "Left Eye", [["eye"], _mappings_left_side]),
	("eye.r", "Right Eye", [["eye"], _mappings_right_side]),

	("shoulder.l", "Left Shoulder", [["shoulder"], _mappings_left_side]),
	("upper_arm.l", "Left Upper Arm", [["upper"], ["arm"], _mappings_left_side]),
	("lower_arm.l", "Left Lower Arm", [["lower"], ["arm"], _mappings_left_side]),
	("wrist.l", "Left Wrist", [["hand", "wrist"], _mappings_left_side]),
	("thumb_1.l", "Left Thumb Proximal", [["thumb"], ["1", "proximal"], _mappings_left_side]),
	("thumb_2.l", "Left Thumb Intermediate", [["thumb"], ["2", "intermediate"], _mappings_left_side]),
	("thumb_3.l", "Left Thumb Distal", [["thumb"], ["3", "distal"], _mappings_left_side]),
	("index_1.l", "Left Index Proximal", [["index"], ["1", "proximal"], _mappings_left_side]),
	("index_2.l", "Left Index Intermediate", [["index"], ["2", "intermediate"], _mappings_left_side]),
	("index_3.l", "Left Index Distal", [["index"], ["3", "distal"], _mappings_left_side]),
	("middle_1.l", "Left Middle Proximal", [["middle"], ["1", "proximal"], _mappings_left_side]),
	("middle_2.l", "Left Middle Intermediate", [["middle"], ["2", "intermediate"], _mappings_left_side]),
	("middle_3.l", "Left Middle Distal", [["middle"], ["3", "distal"], _mappings_left_side]),
	("ring_1.l", "Left Ring Proximal", [["ring"], ["1", "proximal"], _mappings_left_side]),
	("ring_2.l", "Left Ring Intermediate", [["ring"], ["2", "intermediate"], _mappings_left_side]),
	("ring_3.l", "Left Ring Distal", [["ring"], ["3", "distal"], _mappings_left_side]),
	("little_1.l", "Left Little Proximal", [["little"], ["1", "proximal"], _mappings_left_side]),
	("little_2.l", "Left Little Intermediate", [["little"], ["2", "intermediate"], _mappings_left_side]),
	("little_3.l", "Left Little Distal", [["little"], ["3", "distal"], _mappings_left_side]),

	("shoulder.r", "Right Shoulder", [["shoulder"], _mappings_right_side]),
	("upper_arm.r", "Right Upper Arm", [["upper"], ["arm"], _mappings_right_side]),
	("lower_arm.r", "Right Lower Arm", [["lower"], ["arm"], _mappings_right_side]),
	("wrist.r", "Right Wrist", [["hand", "wrist"], _mappings_right_side]),
	("thumb_1.r", "Right Thumb Proximal", [["thumb"], ["1", "proximal"], _mappings_right_side]),
	("thumb_2.r", "Right Thumb Intermediate", [["thumb"], ["2", "intermediate"], _mappings_right_side]),
	("thumb_3.r", "Right Thumb Distal", [["thumb"], ["3", "distal"], _mappings_right_side]),
	("index_1.r", "Right Index Proximal", [["index"], ["1", "proximal"], _mappings_right_side]),
	("index_2.r", "Right Index Intermediate", [["index"], ["2", "intermediate"], _mappings_right_side]),
	("index_3.r", "Right Index Distal", [["index"], ["3", "distal"], _mappings_right_side]),
	("middle_1.r", "Right Middle Proximal", [["middle"], ["1", "proximal"], _mappings_right_side]),
	("middle_2.r", "Right Middle Intermediate", [["middle"], ["2", "intermediate"], _mappings_right_side]),
	("middle_3.r", "Right Middle Distal", [["middle"], ["3", "distal"], _mappings_right_side]),
	("ring_1.r", "Right Ring Proximal", [["ring"], ["1", "proximal"], _mappings_right_side]),
	("ring_2.r", "Right Ring Intermediate", [["ring"], ["2", "intermediate"], _mappings_right_side]),
	("ring_3.r", "Right Ring Distal", [["ring"], ["3", "distal"], _mappings_right_side]),
	("little_1.r", "Right Little Proximal", [["little"], ["1", "proximal"], _mappings_right_side]),
	("little_2.r", "Right Little Intermediate", [["little"], ["2", "intermediate"], _mappings_right_side]),
	("little_3.r", "Right Little Distal", [["little"], ["3", "distal"], _mappings_right_side]),

	("upper_leg.l", "Left Upper Leg", [["leg"], ["upper"], _mappings_left_side]),
	("lower_leg.l", "Left Lower Leg", [["leg"], ["lower"], _mappings_left_side]),
	("foot.l", "Left Foot", [["foot"], _mappings_left_side]),
	("toes.l", "Left Toes", [["toes"], _mappings_left_side]),

	("upper_leg.r", "Right Upper Leg", [["leg"], ["upper"], _mappings_right_side]),
	("lower_leg.r", "Right Lower Leg", [["leg"], ["lower"], _mappings_right_side]),
	("foot.r", "Right Foot", [["foot"], _mappings_right_side]),
	("toes.r", "Right Toes", [["toes"], _mappings_right_side]),
]

def _get_display_name(humanoid_name: str) -> str:
	for bone in _humanoid_bones:
		if(bone[0] == humanoid_name):
			return bone[1]
	return None


class HumanoidBone(bpy.types.PropertyGroup):
	#humanoid_name: bpy.props.EnumProperty(items=_humanoid_bones, name="Humanoid Name", description="E.g. 'Hip', 'LeftUpperArm', 'LeftFingerIndex1', ...") # type: ignore
	bone: bpy.props.StringProperty(name="Bone", description="Bone on the Armature that maps onto the humanoid name") # type: ignore
	# todo rotation limits


class STFEXP_Armature_Humanoid(STF_BlenderComponentBase):
	locomotion_type: bpy.props.EnumProperty(items=[("planti", "Plantigrade", ""),("digi", "Digitigrade", "")], name="Locomotion Type", default="planti") # type: ignore
	no_jaw: bpy.props.BoolProperty(name="Ignore Jaw Mapping", default=False) # type: ignore

	bone_mappings: bpy.props.CollectionProperty(type=HumanoidBone, name="Humanoid Mappings") # type: ignore
	active_bone_mapping: bpy.props.IntProperty() # type: ignore


def _setup_humanoid_collection(component: STFEXP_Armature_Humanoid):
	component.bone_mappings.clear()
	for bone in _humanoid_bones:
		mapping: HumanoidBone = component.bone_mappings.add()
		mapping.name = bone[0]

def _map_humanoid_bones(component: STFEXP_Armature_Humanoid, armature: bpy.types.Armature):
	if(len(component.bone_mappings) != len(_humanoid_bones)):
		_setup_humanoid_collection(component)
	
	for bone_mapping in _humanoid_bones:
		and_conditions = bone_mapping[2]
		candidate = None
		for bone in armature.bones:
			for and_condition in and_conditions:
				for or_condition in and_condition:
					if(or_condition in bone.name.lower()):
						break
				else:
					break
			else:
				if(not candidate or len(candidate) > len(bone.name)):
					candidate = bone.name
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
	def poll(cls, context):
		return context.armature is not None
	
	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
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
	def poll(cls, context):
		return context.armature is not None
	
	def invoke(self, context, event):
		return context.window_manager.invoke_confirm(self, event)

	def execute(self, context):
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

	def draw_item(self, context, layout: bpy.types.UILayout, data, item, icon, active_data, active_propname, index):
		layout.label(text=_get_display_name(item.name), icon="NONE" if item.bone else "ERROR")
		layout.label(text=item.bone if item.bone else "Not Mapped!")

def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: bpy.types.Armature, component: STFEXP_Armature_Humanoid):
	layout.use_property_split = True
	layout.prop(component, "locomotion_type")
	layout.prop(component, "no_jaw")

	layout.separator(factor=2, type="LINE")

	row = layout.row()
	row.operator(ResetHumanoidCollectionOperator.bl_idname, icon="WARNING_LARGE")
	row.operator(MapHumanoidCollectionOperator.bl_idname)

	mapped = 0
	for mapping in component.bone_mappings:
		if(mapping.bone and mapping.bone in context_object.bones):
			mapped += 1
	if(mapped < len(_humanoid_bones)):
		layout.label(text=f"Mapped {mapped} of {len(_humanoid_bones)} Bones.", icon="WARNING_LARGE")

	layout.template_list(STFEXP_HumanoidMappingsList.bl_idname, "", component, "bone_mappings", component, "active_bone_mapping")
	if(len(component.bone_mappings) > component.active_bone_mapping):
		layout.prop_search(component.bone_mappings[component.active_bone_mapping], "bone", context_object, "bones")
		layout.label(text="Muscle limits TBD")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	component: STFEXP_Armature_Humanoid = component
	import_component_base(component, json_resource)

	component.locomotion_type = json_resource.get("locomotion_type", "planti")
	component.no_jaw = json_resource.get("no_jaw", False)

	if("mappings" in json_resource):
		_setup_humanoid_collection(component)
		for humanoid_name, mapping in json_resource["mappings"].items():
			if("target" in mapping and humanoid_name in component.bone_mappings):
				if(target := context.get_imported_resource(mapping["target"])):
					component.bone_mappings[humanoid_name].bone = target.get_bone().name

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Armature_Humanoid, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["locomotion_type"] = component.locomotion_type
	ret["no_jaw"] = component.no_jaw

	mappings: dict[str, dict] = {}
	for mapping in component.bone_mappings:
		if(mapping.bone):
			mappings[mapping.name] = {
				"target": context_object.bones[mapping.bone].stf_info.stf_id
			}
	if(len(mappings) > 0):
		ret["mappings"] = mappings

	return ret, component.stf_id


class STF_Module_STFEXP_Armature_Humanoid(STF_BlenderComponentModule):
	"""Declares that this Armature is humanoid. Must satisfy the requirements for the Unity/VRM humanoid rig"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = []
	understood_application_types = [STFEXP_Armature_Humanoid]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Armature]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_STFEXP_Armature_Humanoid
]


def register():
	setattr(bpy.types.Armature, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Armature_Humanoid))

def unregister():
	if hasattr(bpy.types.Armature, _blender_property_name):
		delattr(bpy.types.Armature, _blender_property_name)
