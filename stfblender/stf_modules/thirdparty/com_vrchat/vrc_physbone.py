import bpy
import json
import re
from typing import Callable

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ....utils.animation_conversion_utils import get_component_stf_path
from ....utils.reference_helper import register_exported_resource, get_resource_id
from ....base.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf
from ....base.blender_grr.stf_node_path_component_selector import NodePathComponentSelector, draw_node_path_component_selector, node_path_component_selector_from_stf, node_path_component_selector_to_stf


_stf_type = "com.vrchat.physbone"
_blender_property_name = "vrc_physbone"

# todo: this is quite jank, make this able to select the object/armature->bone/component etc..
class VRC_Physbone(STF_BlenderComponentBase):
	ignores: bpy.props.CollectionProperty(type=NodePathSelector, name="Ignored Children", options=set()) # type: ignore
	colliders: bpy.props.CollectionProperty(type=NodePathComponentSelector, name="Colliders", options=set()) # type: ignore
	values: bpy.props.StringProperty(name="Json Values", options=set()) # type: ignore


class Edit_VRC_Physbone(bpy.types.Operator):
	bl_idname = "stf.edit_vrc_physbone"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore
	blender_bone: bpy.props.BoolProperty() # type: ignore

	op: bpy.props.StringProperty() # type: ignore
	property: bpy.props.StringProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		if(self.op == "add"):
			if(not self.blender_bone):
				for pb in context.object.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).add()
						return {"FINISHED"}
			else:
				for pb in context.bone.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).add()
						return {"FINISHED"}
		elif(self.op == "remove"):
			if(not self.blender_bone):
				for pb in context.object.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).remove(self.index)
						return {"FINISHED"}
			else:
				for pb in context.bone.vrc_physbone:
					if(pb.stf_id == self.component_id):
						getattr(pb, self.property).remove(self.index)
						return {"FINISHED"}
		self.report({"ERROR"}, "Couldn't edit Physbone")
		return {"CANCELLED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_Physbone):
	box = layout.box().column(align=True)
	row = box.row()
	row.label(text="Colliders")
	add_button = row.operator(Edit_VRC_Physbone.bl_idname, text="Add", icon="ADD")
	add_button.blender_bone = type(component.id_data) == bpy.types.Armature
	add_button.component_id = component.stf_id
	add_button.op = "add"
	add_button.property = "colliders"
	box.separator(factor=1)
	for index, collider in enumerate(component.colliders):
		if(index > 0):
			box.separator(factor=1)
		row = box.row(align=True)
		col = row.column(align=True)
		col.use_property_split = True
		draw_node_path_component_selector(col, collider)
		remove_button = row.operator(Edit_VRC_Physbone.bl_idname, text="", icon="X")
		remove_button.blender_bone = type(component.id_data) == bpy.types.Armature
		remove_button.component_id = component.stf_id
		remove_button.op = "remove"
		remove_button.index = index
		remove_button.property = "colliders"

	box = layout.box().column(align=True)
	row = box.row()
	row.label(text="Ignores")
	add_button = row.operator(Edit_VRC_Physbone.bl_idname, text="Add", icon="ADD")
	add_button.blender_bone = type(component.id_data) == bpy.types.Armature
	add_button.component_id = component.stf_id
	add_button.op = "add"
	add_button.property = "ignores"
	box.separator(factor=1)
	for index, ignore in enumerate(component.ignores):
		row = box.row(align=True)
		draw_node_path_selector(row, ignore)
		remove_button = row.operator(Edit_VRC_Physbone.bl_idname, text="", icon="X")
		remove_button.blender_bone = type(component.id_data) == bpy.types.Armature
		remove_button.component_id = component.stf_id
		remove_button.op = "remove"
		remove_button.index = index
		remove_button.property = "ignores"

	layout.separator(factor=1)
	col = layout.column(align=True)
	col.label(text="Json Data:", icon="PASTEDOWN")
	json_error = False
	try:
		json.loads(component.values)
	except:
		json_error = True
	col.alert = json_error
	col.prop(component, "values", text="", icon="ERROR" if json_error else "NONE")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, context_object)
	component.values = json.dumps(json_resource["values"])

	_get_component = preserve_component_reference(component, context_object)
	def _handle():
		component = _get_component()
		for ignore_path in json_resource.get("ignores", []):
			print(ignore_path)
			new_ignore = component.ignores.add()
			node_path_selector_from_stf(context, json_resource, ignore_path, new_ignore)

		for collider_path in json_resource.get("colliders", []):
			print(collider_path)
			new_collider = component.colliders.add()
			node_path_component_selector_from_stf(context, json_resource, collider_path, new_collider)

	context.add_task(_handle)

	return component


def _stf_export(context: STF_ExportContext, component: VRC_Physbone, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	try:
		ret["values"] = json.loads(component.values)

		_get_component = preserve_component_reference(component, context_object)
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
		context.add_task(_handle)

		return ret, component.stf_id
	except Exception:
		return None


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[list[float]], list[float]], list[int]]:
	if(match := re.search(r"^vrc_physbone\[(?P<component_index>[\d]+)\].enabled", data_path)):
		component = application_object.vrc_physbone[int(match.groupdict()["component_index"])]
		component_path = get_component_stf_path(application_object, component)
		if(component_path):
			return component_path + ["enabled"], None, None
	return None

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	# let component_index
	for component_index, component in enumerate(application_object.vrc_physbone):
		if(component.stf_id == blender_object.stf_id):
			break
	match(stf_path[1]):
		case "enabled":
			return None, 0, "OBJECT", "vrc_physbone[" + str(component_index) + "].enabled", None, None
	return None


class STF_Module_VRC_Physbone(STF_BlenderComponentModule):
	"""Represents a `VRCPhysbone`. Serialize the component in Unity and paste the Json-definition into the `Json Values` field.
	You must manually set the ID's of referenced Collider components and the Objects/Bones that should be ignored by the Physbone"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["secondary_motion"]
	understood_application_types = [VRC_Physbone]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = [_blender_property_name]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_VRC_Physbone
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=VRC_Physbone))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=VRC_Physbone))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
