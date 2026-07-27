import bpy
import json
import re
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_TaskSteps, STF_Category, STFReport, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Component_Ref, STF_Handler_Animation, add_component, export_component_base, import_component_base, preserve_component_reference
from .....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from .....stfblender_common.helpers import create_add_button, create_remove_button
from .....stfblender_common.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf
from .....stfblender_common.blender_grr.stf_node_path_component_selector import NodePathComponentSelector, draw_node_path_component_selector, node_path_component_selector_from_stf, node_path_component_selector_to_stf


class VRC_Physbone(STF_ComponentResourceBase):
	ignores: bpy.props.CollectionProperty(type=NodePathSelector, name="Ignored Children", options=set())
	colliders: bpy.props.CollectionProperty(type=NodePathComponentSelector, name="Colliders", options=set())
	values: bpy.props.StringProperty(name="Json Values", options=set())


class Handler_VRC_Physbone(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""Represents a `VRCPhysbone`. Serialize the component in Unity and paste the Json-definition into the `Json Values` field.
	You must manually set the ID's of referenced Collider components and the Objects/Bones that should be ignored by the Physbone"""
	stf_type = "com.vrchat.physbone"
	stf_category = STF_Category.COMPONENT
	like_types = ["secondary_motion"]
	understood_blender_types = [VRC_Physbone]
	blender_property_name = "vrc_physbone"
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "VRChat Physbone"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: VRC_Physbone):
		box = layout.box().column(align=True)
		row = box.row()
		row.label(text="Colliders")
		create_add_button(row, "bone" if type(component.id_data) is bpy.types.Armature else "object", cls.blender_property_name, component.stf_id, "colliders")
		box.separator(factor=1)
		for index, collider in enumerate(component.colliders):
			if(index > 0):
				box.separator(factor=1, type="LINE")
			row = box.row(align=True)
			col = row.column(align=True)
			col.use_property_split = True
			draw_node_path_component_selector(col, collider)
			create_remove_button(row, "bone" if type(component.id_data) is bpy.types.Armature else "object", cls.blender_property_name, component.stf_id, "colliders", index)

		box = layout.box().column(align=True)
		row = box.row()
		row.label(text="Ignores")
		create_add_button(row, "bone" if type(component.id_data) is bpy.types.Armature else "object", cls.blender_property_name, component.stf_id, "ignores")
		box.separator(factor=1)
		for index, ignore in enumerate(component.ignores):
			row = box.row(align=True)
			draw_node_path_selector(row, ignore)
			create_remove_button(row, "bone" if type(component.id_data) is bpy.types.Armature else "object", cls.blender_property_name, component.stf_id, "ignores", index)

		layout.separator(factor=1)
		col = layout.column(align=True)
		col.label(text="Json Data:", icon="PASTEDOWN")
		json_error = False
		try:
			json.loads(component.values)
		except Exception:
			json_error = True
		col.alert = json_error
		col.prop(component, "values", text="", icon="ERROR" if json_error else "NONE")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		component.values = json.dumps(json_resource["values"])

		_get_component = preserve_component_reference(component, cls.blender_property_name, context_resource)
		def _handle():
			component = _get_component()
			for ignore_path in json_resource.get("ignores", []):
				new_ignore = component.ignores.add()
				node_path_selector_from_stf(context, json_resource, ignore_path, new_ignore)

			for collider_path in json_resource.get("colliders", []):
				new_collider = component.colliders.add()
				node_path_component_selector_from_stf(context, json_resource, collider_path, new_collider)

		context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: VRC_Physbone, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		try:
			ret["values"] = json.loads(component.values)

			_get_component = preserve_component_reference(component, cls.blender_property_name, context_resource)
			def _handle():
				component = _get_component()

				ignores = []
				for ignore in component.ignores:
					if(ignore_ret := node_path_selector_to_stf(context, ignore, ret)):
						ignores.append(ignore_ret)
				ret["ignores"] = ignores

				colliders = []
				for collider in component.colliders:
					if(collider_ret := node_path_component_selector_to_stf(context, collider, ret)):
						colliders.append(collider_ret)
				ret["colliders"] = colliders
			context.add_task(STF_TaskSteps.DEFAULT, _handle)

			return ret, component.stf_id
		except Exception:
			return None # pyright: ignore[reportReturnType]

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [blender_property_name]

	@classmethod
	def export_blender_animation(cls, context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
		if(match := re.search(r"^" + cls.blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
			if(component_path := get_component_stf_path_from_collection(blender_resource, cls.blender_property_name, int(match.groupdict()["component_index"]))):
				return STFPropertyPathPart(component_path + ["enabled"])
		return None

	@classmethod
	def import_stf_animation(cls, context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
		blender_object = context.get_imported_resource(stf_property_path[0])
		component_index = get_component_index(blender_resource, cls.blender_property_name, blender_object.stf_id)
		if(component_index is not None):
			match(stf_property_path[1]):
				case "enabled":
					return BlenderPropertyPathPart("OBJECT", cls.blender_property_name + "[" + str(component_index) + "].enabled")
		return None


def register():
	setattr(bpy.types.Object, Handler_VRC_Physbone.blender_property_name, bpy.props.CollectionProperty(type=VRC_Physbone))
	setattr(bpy.types.Bone, Handler_VRC_Physbone.blender_property_name, bpy.props.CollectionProperty(type=VRC_Physbone))

def unregister():
	if hasattr(bpy.types.Object, Handler_VRC_Physbone.blender_property_name):
		delattr(bpy.types.Object, Handler_VRC_Physbone.blender_property_name)
	if hasattr(bpy.types.Bone, Handler_VRC_Physbone.blender_property_name):
		delattr(bpy.types.Bone, Handler_VRC_Physbone.blender_property_name)
