import bpy
import json
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base


class VRC_AvatarColliders(STF_ComponentResourceBase):
	data: bpy.props.StringProperty(name="Data", options=set())


class Handler_VRC_AvatarColliders(STF_Handler_Component):
	"""Represents the `Colliders` of an `VRCAvatarDescriptor`.
	Serialize the component in Unity and paste the Json-definition into the `Data` field"""
	stf_type = "com.vrchat.avatar_colliders"
	stf_category = STF_Category.COMPONENT
	like_types = []
	understood_blender_types = [VRC_AvatarColliders]
	blender_property_name = "com_vrchat_avatar_colliders"
	single = True
	filter = [bpy.types.Collection]
	pretty_name_template = "VRChat Avatar Colliders"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: VRC_AvatarColliders):
		col = layout.column(align=True)
		col.label(text="Json Data:", icon="PASTEDOWN")

		json_error = False
		try:
			json.loads(component.data)
		except Exception:
			json_error = True
		col.alert = json_error
		col.prop(component, "data", text="", icon="ERROR" if json_error else "NONE")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		component.data = json.dumps(json_resource["values"])
		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: VRC_AvatarColliders, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		try:
			ret["values"] = json.loads(component.data)
			return ret, component.stf_id
		except Exception:
			return None # pyright: ignore[reportReturnType]


def register():
	setattr(bpy.types.Collection, Handler_VRC_AvatarColliders.blender_property_name, bpy.props.CollectionProperty(type=VRC_AvatarColliders))

def unregister():
	if hasattr(bpy.types.Collection, Handler_VRC_AvatarColliders.blender_property_name):
		delattr(bpy.types.Collection, Handler_VRC_AvatarColliders.blender_property_name)
