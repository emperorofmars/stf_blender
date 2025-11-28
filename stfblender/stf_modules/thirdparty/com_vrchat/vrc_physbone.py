import bpy
import json
import re

from ....base.stf_task_steps import STF_TaskSteps
from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ....utils.animation_conversion_utils import get_component_index, get_component_stf_path, get_component_stf_path_from_collection
from ....base.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf
from ....base.blender_grr.stf_node_path_component_selector import NodePathComponentSelector, draw_node_path_component_selector, node_path_component_selector_from_stf, node_path_component_selector_to_stf
from ....utils.helpers import create_add_button, create_remove_button
from ....base.property_path_part import BlenderPropertyPathPart, STFPropertyPathPart


_stf_type = "com.vrchat.physbone"
_blender_property_name = "vrc_physbone"

# todo: this is quite jank, make this able to select the object/armature->bone/component etc..
class VRC_Physbone(STF_BlenderComponentBase):
	ignores: bpy.props.CollectionProperty(type=NodePathSelector, name="Ignored Children", options=set()) # type: ignore
	colliders: bpy.props.CollectionProperty(type=NodePathComponentSelector, name="Colliders", options=set()) # type: ignore
	values: bpy.props.StringProperty(name="Json Values", options=set()) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: VRC_Physbone):
	box = layout.box().column(align=True)
	row = box.row()
	row.label(text="Colliders")
	create_add_button(row, "bone" if type(component.id_data) == bpy.types.Armature else "object", _blender_property_name, component.stf_id, "colliders")
	box.separator(factor=1)
	for index, collider in enumerate(component.colliders):
		if(index > 0):
			box.separator(factor=1, type="LINE")
		row = box.row(align=True)
		col = row.column(align=True)
		col.use_property_split = True
		draw_node_path_component_selector(col, collider)
		create_remove_button(row, "bone" if type(component.id_data) == bpy.types.Armature else "object", _blender_property_name, component.stf_id, "colliders", index)

	box = layout.box().column(align=True)
	row = box.row()
	row.label(text="Ignores")
	create_add_button(row, "bone" if type(component.id_data) == bpy.types.Armature else "object", _blender_property_name, component.stf_id, "ignores")
	box.separator(factor=1)
	for index, ignore in enumerate(component.ignores):
		row = box.row(align=True)
		draw_node_path_selector(row, ignore)
		create_remove_button(row, "bone" if type(component.id_data) == bpy.types.Armature else "object", _blender_property_name, component.stf_id, "ignores", index)

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
			new_ignore = component.ignores.add()
			node_path_selector_from_stf(context, json_resource, ignore_path, new_ignore)

		for collider_path in json_resource.get("colliders", []):
			new_collider = component.colliders.add()
			node_path_component_selector_from_stf(context, json_resource, collider_path, new_collider)

	context.add_task(STF_TaskSteps.DEFAULT, _handle)

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
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return ret, component.stf_id
	except Exception:
		return None


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> BlenderPropertyPathPart:
	blender_object = context.get_imported_resource(stf_path[0])
	if(component_index := get_component_index(application_object, _blender_property_name, blender_object.stf_id)):
		match(stf_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
	return None


"""Module definition"""

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
