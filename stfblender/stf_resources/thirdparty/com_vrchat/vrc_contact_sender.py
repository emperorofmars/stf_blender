import bpy
from typing import Any

from .vrc_contact_base import VRC_ContactBase, vrc_contact_create_export_blender_animation, vrc_contact_create_import_stf_animation, vrc_contact_draw_base, vrc_contact_export_base, vrc_contact_import_base
from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_Handler_BoneComponent, STF_Component_Ref, ComponentLoadJsonOperatorBase, add_component, export_component_base, import_component_base


_stf_type = "com.vrchat.contact_sender"
_blender_property_name = "com_vrchat_contact_sender"


class VRC_ContactSender(VRC_ContactBase):
	pass


class VRC_ContactSender_LoadJsonOperator(ComponentLoadJsonOperatorBase, bpy.types.Operator):
	bl_idname = "stf.vrc_contact_sender_loadjson"

	blender_bone: bpy.props.BoolProperty()

	def get_property(self, context) -> Any:
		if(not self.blender_bone):
			return getattr(context.object, _blender_property_name)
		else:
			return getattr(context.bone, _blender_property_name)

	def parse_json(self, context: bpy.types.Context, component: Any, json_resource: dict):
		if(json_resource.get("type") != _stf_type): raise Exception("Invalid Type")
		vrc_contact_import_base(component, json_resource)


class Handler_VRC_ContactSender(STF_Handler_BoneComponent):
	"""Represents a `VRCContactSender`.
	Serialize the component in Unity and paste the Json-definition into the `Set from JSON` operator"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = []
	understood_blender_types = [VRC_ContactSender]
	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "VRChat Contact Sender"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: VRC_ContactSender):
		layout.use_property_split = True
		vrc_contact_draw_base(layout, context, component_ref, context_resource, component, cls.blender_property_name)

		load_json_button = layout.operator(VRC_ContactSender_LoadJsonOperator.bl_idname)
		load_json_button.blender_bone = type(component.id_data) is bpy.types.Armature
		load_json_button.component_id = component.stf_id

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		vrc_contact_import_base(component, json_resource) # pyright: ignore[reportArgumentType]
		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: VRC_ContactSender, context_resource: Any) -> tuple[dict, str]:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		vrc_contact_export_base(component, context_resource, ret)
		return ret, component.stf_id

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [blender_property_name]
	export_blender_animation = vrc_contact_create_export_blender_animation(blender_property_name)
	import_stf_animation = vrc_contact_create_import_stf_animation(blender_property_name)


def register():
	setattr(bpy.types.Object, Handler_VRC_ContactSender.blender_property_name, bpy.props.CollectionProperty(type=VRC_ContactSender, options=set()))
	setattr(bpy.types.Bone, Handler_VRC_ContactSender.blender_property_name, bpy.props.CollectionProperty(type=VRC_ContactSender, options=set()))

def unregister():
	if hasattr(bpy.types.Bone, Handler_VRC_ContactSender.blender_property_name):
		delattr(bpy.types.Bone, Handler_VRC_ContactSender.blender_property_name)
	if hasattr(bpy.types.Object, Handler_VRC_ContactSender.blender_property_name):
		delattr(bpy.types.Object, Handler_VRC_ContactSender.blender_property_name)
