import bpy

from ...utils.reference_helper import register_exported_resource


class NodePathSelector(bpy.types.PropertyGroup):
	target_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Object") # type: ignore
	target_bone: bpy.props.StringProperty(name="Bone (Optional)") # type: ignore


def draw_node_path_selector(layout: bpy.types.UILayout, nps: NodePathSelector):
	if(type(nps.id_data) == bpy.types.Armature):
		layout.prop_search(nps, "target_bone", nps.id_data, "bones", text="Target")
	else:
		layout.prop(nps, "target_object")
		if(nps.target_object and type(nps.target_object.data) == bpy.types.Armature):
			layout.prop_search(nps, "target_bone", nps.target_object.data, "bones")


def resolve_node_path_selector(nps: NodePathSelector) -> bpy.types.Object | bpy.types.Bone | None:
	if(type(nps.id_data) == bpy.types.Object and nps.target_object):
		if(type(nps.target_object.data) == bpy.types.Armature):
			if(not nps.target_bone):
				return nps.target_object
			elif(nps.target_bone and nps.target_object in nps.target_object.data.bones):
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


def node_path_selector_to_stf(nps: NodePathSelector, json_resource: dict) -> list[str]:
	if(type(nps.id_data) == bpy.types.Object and nps.target_object):
		if(type(nps.target_object.data) == bpy.types.Armature):
			if(not nps.target_bone):
				return [register_exported_resource(json_resource, nps.target_object.stf_info.stf_id)]
			elif(nps.target_bone and nps.target_object in nps.target_object.data.bones):
				return [register_exported_resource(json_resource, nps.target_object.stf_info.stf_id), "instance", register_exported_resource(json_resource, nps.target_object.data.bones[nps.target_bone].stf_info.stf_id)]
			else:
				return None
		else:
			return [register_exported_resource(json_resource, nps.target_object.stf_info.stf_id)]
	elif(type(nps.id_data) == bpy.types.Armature and nps.target_bone and nps.target_bone in nps.id_data.bones):
		return [register_exported_resource(json_resource, nps.id_data.bones[nps.target_bone].stf_info.stf_id)]
	else:
		return None


def node_path_selector_from_stf(nps: NodePathSelector, context_object: bpy.types.Object | bpy.types.Bone):
	pass
