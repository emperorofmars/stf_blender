from typing import Callable
import bpy

from ....base.property_path_part import STFPropertyPathPart

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....base.stf_module import STF_Module
from ....utils.id_utils import ensure_stf_id
from ....base.stf_report import STFReportSeverity, STFReport
from ....utils.component_utils import get_components_from_object
from .stf_instance_mesh_util import set_instance_blendshapes


_stf_type = "stf.instance.mesh"


class STF_Instance_Mesh_Blendshape_Value(bpy.types.PropertyGroup):
	name: bpy.props.StringProperty(name="Name", options=set()) # type: ignore
	override: bpy.props.BoolProperty(name="Override", default=False, options=set()) # type: ignore
	value: bpy.props.FloatProperty(name="Value", default=0, soft_min=0, soft_max=1, subtype="FACTOR") # type: ignore

class STF_Instance_Mesh(bpy.types.PropertyGroup):
	override_blendshape_values: bpy.props.BoolProperty(name="Override Blendshape Values", default=False, options=set()) # type: ignore
	blendshape_values: bpy.props.CollectionProperty(type=STF_Instance_Mesh_Blendshape_Value, name="Blendshape Values", options=set()) # type: ignore
	active_blendshape: bpy.props.IntProperty(options=set()) # type: ignore


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_resource = context.import_resource(json_resource["mesh"], stf_kind="data")
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_resource)
	blender_object.stf_instance.stf_id = stf_id
	if(json_resource.get("name")):
		blender_object.stf_instance.stf_name = json_resource["name"]
	context.register_imported_resource(stf_id, (blender_object, blender_resource))

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import mesh: " + str(json_resource.get("instance", {}).get("mesh")), STFReportSeverity.Error, stf_id, _stf_type, context_object))

	if("armature_instance" in json_resource):
		armature_instance: bpy.types.Object = context.import_resource(json_resource["armature_instance"], stf_kind="node")
		if(not armature_instance):
			context.report(STFReport("Invalid armature instance: " + str(json_resource["armature_instance"]), STFReportSeverity.Error, stf_id, _stf_type, context_object))
		else:
			modifier: bpy.types.ArmatureModifier = blender_object.modifiers.new("Armature", "ARMATURE")
			modifier.object = armature_instance

	# blendshape values per instance
	if("blendshape_values" in json_resource):
		set_instance_blendshapes(blender_object)
		blender_object.stf_instance_mesh.override_blendshape_values = True
		for index, blendshape_value in enumerate(json_resource["blendshape_values"]):
			instance_blendshape = blender_object.stf_instance_mesh.blendshape_values[index + 1]
			if(blendshape_value != None):
				instance_blendshape.value = blendshape_value
				instance_blendshape.override = True

	if("materials" in json_resource):
		for material_index, material_id in enumerate(json_resource["materials"]):
			if(material_id and len(blender_object.material_slots) > material_index):
				if(material := context.import_resource(material_id, stf_kind="data")):
					blender_object.material_slots[material_index].link = "OBJECT"
					blender_object.material_slots[material_index].material = material

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and type(application_object[1]) == bpy.types.Mesh):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, application_object: any, context_object: bpy.types.Collection) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_mesh: bpy.types.Mesh = application_object[1]
	
	ensure_stf_id(context, blender_object.stf_instance)
	ret = {"type": _stf_type, "name": blender_object.stf_instance.stf_name}

	blender_object.update_from_editmode()

	blender_armatures: list[bpy.types.ArmatureModifier] = []
	for _, modifier in blender_object.modifiers.items():
		if(type(modifier) is bpy.types.ArmatureModifier):
			blender_armatures.append(modifier)

	if(len(blender_armatures) == 1 and blender_armatures[0] and blender_armatures[0].object and blender_armatures[0].object.data):
		if(not context_object.is_embedded_data and context_object not in blender_armatures[0].object.users_collection):
			context.report(STFReport("Armature sits outside the exported asset", severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_info.stf_id, stf_type=_stf_type, application_object=blender_object))
			return None
		# The armature has to be passed, because in Blenders datamodel, the relationship between mesh and armature is loose.
		ret["mesh"] = context.serialize_resource(blender_mesh, blender_armatures[0].object.data, module_kind="data")
		ret["armature_instance"] = context.serialize_resource(blender_armatures[0].object, module_kind="node")
	elif(len(blender_armatures) > 1):
		context.report(STFReport("More than one Armature per mesh is not supported!", severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_info.stf_id, stf_type=_stf_type, application_object=blender_object))
		return None
	else:
		ret["mesh"] = context.serialize_resource(blender_mesh, module_kind="data")

	material_slots = []
	for material_slot in blender_object.material_slots:
		if(material_slot.material and material_slot.link == "OBJECT"):
			material_slots.append(context.serialize_resource(material_slot.material, module_kind="data"))
		else:
			material_slots.append(None)
	ret["materials"] = material_slots

	if(blender_mesh.shape_keys and len(blender_mesh.shape_keys.key_blocks) > 1 and blender_object.stf_instance_mesh.override_blendshape_values):
		blendshape_values = []
		for blendshape in blender_mesh.shape_keys.key_blocks[1:]:
			for instance_blendshape in blender_object.stf_instance_mesh.blendshape_values:
				if(instance_blendshape.name == blendshape.name):
					blendshape_values.append(instance_blendshape.value if instance_blendshape.override else None)
					break
			else:
				blendshape_values.append(None)
		ret["blendshape_values"] = blendshape_values

	return ret, blender_object.stf_instance.stf_id


def _resolve_property_path_to_stf_func(context: STF_ExportContext, blender_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	import re
	match = re.search(r"^key_blocks\[\"(?P<blendshape_name>[\w. -:,]+)\"\].value", data_path)
	if(match and "blendshape_name" in match.groupdict()):
		return STFPropertyPathPart([blender_object.stf_info.stf_id, "instance", "blendshape", match.groupdict()["blendshape_name"], "value"])
	return None

def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], blender_object: bpy.types.Object) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	if(len(stf_path) == 4 and stf_path[1] == "blendshape" and stf_path[3] == "value"):
		return None, 0, "KEY", "key_blocks[\"" + stf_path[2] + "\"].value", None, None
	elif(len(stf_path) >= 5 and stf_path[1] == "material"):
		material_index = int(stf_path[2])
		if(len(blender_object.material_slots) <= material_index or not blender_object.material_slots[material_index].material):
			return None
		module_ret = context.resolve_stf_property_path([blender_object.material_slots[material_index].material.stf_info.stf_id] + stf_path[2:], blender_object)
		if(module_ret):
			target_object, _application_object_property_index, slot_type, fcurve_target, index_table, conversion_func = module_ret # Ignore Target Object for now
			return blender_object, material_index, slot_type, fcurve_target, index_table, conversion_func
	return None


class STF_Module_STF_Instance_Mesh(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["instance.mesh", "instance"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["key_blocks"]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Instance_Mesh
]


def register():
	bpy.types.Object.stf_instance_mesh = bpy.props.PointerProperty(type=STF_Instance_Mesh, options=set()) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stf_instance_mesh"):
		del bpy.types.Object.stf_instance_mesh
