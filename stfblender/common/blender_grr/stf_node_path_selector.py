import bpy
from collections.abc import Sequence
from typing import Any

from .. import STF_ImportContext, STF_ExportContext, STF_Category
from ..helpers import register_exported_resource


class NodePathSelector(bpy.types.PropertyGroup):
	target_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Object") # type: ignore
	target_bone: bpy.props.StringProperty(name="Bone") # type: ignore


def draw_node_path_selector(layout: bpy.types.UILayout, nps: NodePathSelector, text: str = "Target"):
	if(type(nps.id_data) == bpy.types.Armature):
		layout.prop_search(nps, "target_bone", nps.id_data, "bones", text=text)
	else:
		layout.prop(nps, "target_object")
		if(nps.target_object and type(nps.target_object.data) == bpy.types.Armature):
			layout.prop_search(nps, "target_bone", nps.target_object.data, "bones")


def resolve_node_path_selector(nps: NodePathSelector) -> bpy.types.Object | bpy.types.Bone | None:
	if(not nps): return None
	if(type(nps.id_data) == bpy.types.Object and nps.target_object):
		if(type(nps.target_object.data) == bpy.types.Armature):
			if(not nps.target_bone):
				return nps.target_object
			elif(nps.target_bone and nps.target_bone in nps.target_object.data.bones):
				return nps.target_object.data.bones[nps.target_bone]
			else:
				return None
		else:
			return nps.target_object
	elif(type(nps.id_data) == bpy.types.Armature and nps.target_bone and nps.target_bone in nps.id_data.bones):
		return nps.id_data.bones[nps.target_bone]
	else:
		return None


def validate_node_path_selector(nps: NodePathSelector) -> bool:
	return resolve_node_path_selector(nps) != None


def node_path_selector_to_string(nps: NodePathSelector) -> str:
	if(not nps): return "Invalid"
	if(type(nps.id_data) == bpy.types.Object and nps.target_object):
		if(type(nps.target_object.data) == bpy.types.Armature):
			if(not nps.target_bone):
				return nps.target_object.name
			elif(nps.target_bone and nps.target_bone in nps.target_object.data.bones):
				return nps.target_object.name + " : " + nps.target_bone
			else:
				return "Invalid"
		else:
			return nps.target_object.name
	elif(type(nps.id_data) == bpy.types.Armature and nps.target_bone and nps.target_bone in nps.id_data.bones):
		return nps.target_bone
	else:
		return "Invalid"


def node_path_selector_to_stf(context: STF_ExportContext, nps: NodePathSelector, json_resource: dict[str, Any]) -> Sequence[str]:
	if(type(nps.id_data) == bpy.types.Object and nps.target_object):
		if(type(nps.target_object.data) == bpy.types.Armature):
			if(not nps.target_bone):
				return [context.serialize_resource(json_resource, nps.target_object, stf_category=STF_Category.NODE)]
			elif(nps.target_bone and nps.target_bone in nps.target_object.data.bones):
				return [context.serialize_resource(json_resource, nps.target_object, stf_category=STF_Category.NODE), STF_Category.INSTANCE, context.serialize_resource(json_resource, nps.target_object.data.bones[nps.target_bone], stf_category=STF_Category.NODE)]
			else:
				return None
		else:
			return [context.serialize_resource(json_resource, nps.target_object, stf_category=STF_Category.NODE)]
	elif(type(nps.id_data) == bpy.types.Armature and nps.target_bone and nps.target_bone in nps.id_data.bones):
		return [context.serialize_resource(json_resource, nps.id_data.bones[nps.target_bone], stf_category=STF_Category.NODE)]
	else:
		return None


def node_path_selector_from_stf(context: STF_ImportContext, json_resource: dict[str, Any], node_path: Sequence[str], nps: NodePathSelector):
	if(type(nps.id_data) == bpy.types.Object):
		if(len(node_path) == 1):
			nps.target_object = context.import_resource(json_resource, node_path[0], STF_Category.NODE)
		if(len(node_path) == 3 and node_path[1] == "instance"):
			nps.target_object = context.import_resource(json_resource, node_path[0], STF_Category.NODE)
			nps.target_bone = context.import_resource(json_resource, node_path[2], STF_Category.NODE).name
	if(type(nps.id_data) == bpy.types.Armature):
		nps.target_bone = context.import_resource(json_resource, node_path[0], STF_Category.NODE).name

