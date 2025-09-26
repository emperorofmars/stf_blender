import bpy

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "stfexp.armature.humanoid"
_blender_property_name = "stfexp_armature_humanoid"


_humanoid_bones = (
	("hip", "Hip", ""),
	("spine", "Spine", ""),
	("chest", "Chest", ""),
	("chest_upper", "Upper Chest", ""),
	("neck", "Neck", ""),
	("head", "Head", ""),
	("jaw", "Jaw", ""),
	("eye_l", "Left Eye", ""),
	("eye_r", "Right Eye", ""),
)

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
	no_jaw: bpy.props.BoolProperty(name="No Jaw Mapping", default=False) # type: ignore

	bone_mappings: bpy.props.CollectionProperty(type=HumanoidBone, name="Humanoid Mappings") # type: ignore
	active_bone_mapping: bpy.props.IntProperty() # type: ignore


def _setup_humanoid_collection(component: STFEXP_Armature_Humanoid):
	component.bone_mappings.clear()
	for bone in _humanoid_bones:
		mapping: HumanoidBone = component.bone_mappings.add()
		mapping.name = bone[0]


class ResetHumanoidCollectionOperator(bpy.types.Operator):
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


class STFEXP_HumanoidMappingsList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stfexp_humanoid_mappings_list"

	def draw_item(self, context, layout: bpy.types.UILayout, data, item, icon, active_data, active_propname, index):
		layout.label(text=_get_display_name(item.name), icon="NONE" if item.bone else "ERROR")
		layout.label(text=item.bone if item.bone else "Not Mapped!")

def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: bpy.types.Armature, component: STFEXP_Armature_Humanoid):
	layout.use_property_split = True
	layout.prop(component, "locomotion_type")
	layout.prop(component, "no_jaw")

	layout.operator(ResetHumanoidCollectionOperator.bl_idname)

	mapped = 0
	for mapping in component.bone_mappings:
		if(mapping.bone and mapping.bone in context_object.bones):
			mapped += 1
	if(mapped < len(_humanoid_bones)):
		layout.label(text=f"Mapped {mapped} of {len(_humanoid_bones)} Bones.", icon="WARNING_LARGE")

	layout.template_list(STFEXP_HumanoidMappingsList.bl_idname, "", component, "bone_mappings", component, "active_bone_mapping")
	if(len(component.bone_mappings) > component.active_bone_mapping):
		layout.prop_search(component.bone_mappings[component.active_bone_mapping], "bone", context_object, "bones")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	component.locomotion_type = json_resource.get("locomotion_type", "planti")
	component.no_jaw = json_resource.get("no_jaw", False)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Armature_Humanoid, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	ret["locomotion_type"] = component.locomotion_type
	ret["no_jaw"] = component.no_jaw
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
