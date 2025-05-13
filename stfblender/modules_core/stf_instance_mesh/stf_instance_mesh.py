import re
from typing import Callable
import uuid
import bpy

from ....libstf.stf_export_context import STF_ExportContext
from ....libstf.stf_import_context import STF_ImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ...utils.component_utils import get_components_from_object


_stf_type = "stf.instance.mesh"


def _translate_property_to_stf_func(blender_object: bpy.types.Object, data_path: str, data_index: int) -> tuple[list[str], Callable[[any], any]]:
	match = re.search(r"^key_blocks\[\"(?P<blendshape_name>[\w]+)\"\].value", data_path)
	if(match and "blendshape_name" in match.groupdict()):
		return [blender_object.stf_id, "instance", "blendshape", match.groupdict()["blendshape_name"], "value"], None

	return None


def _translate_property_to_blender_func(blender_object: bpy.types.Object, stf_property: str) -> tuple[str, int, Callable[[any], any]]:
	return stf_property, 0, None


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_resource = context.import_resource(json_resource["mesh"], stf_kind="data")
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_resource)
	context.register_imported_resource(stf_id, blender_object)

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import mesh: " + str(json_resource.get("instance", {}).get("mesh")), STFReportSeverity.Error, stf_id, _stf_type, context_object))

	if("armature_instance" in json_resource):
		armature_instance: bpy.types.Object = context.import_resource(json_resource["armature_instance"], stf_kind="node")
		if(not armature_instance):
			context.report(STFReport("Invalid armature instance: " + str(json_resource["armature_instance"]), STFReportSeverity.Error, stf_id, _stf_type, context_object))
		else:
			modifier: bpy.types.ArmatureModifier = blender_object.modifiers.new("Armature", "ARMATURE")
			modifier.object = armature_instance

	# TODO handle materials, blendshape values

	return blender_object


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == tuple and type(application_object[0]) == bpy.types.Object and type(application_object[1]) == bpy.types.Mesh):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_object: bpy.types.Object = application_object[0]
	blender_mesh: bpy.types.Mesh = application_object[1]
	ret = {"type": _stf_type}

	blender_object.update_from_editmode()

	blender_armatures: list[bpy.types.ArmatureModifier] = []
	for _, modifier in blender_object.modifiers.items():
		if(type(modifier) is bpy.types.ArmatureModifier):
			blender_armatures.append(modifier)

	if(len(blender_armatures) == 1):
		if(blender_armatures[0].object.stf_id):
			# TODO check if the armature is in the export and within the same hierarchy, otherwise check if its in an instanced hierarchy

			# The armature has to be passed, because in Blenders datamodel the relationship between mesh and armature loose.
			ret["mesh"] = context.serialize_resource(blender_mesh, blender_armatures[0].object.data, module_kind="data")
			ret["armature_instance"] = context.serialize_resource(blender_armatures[0].object, module_kind="node")
		else:
			context.report(STFReport("Invalid armature: " + str(blender_armatures[0].object), severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_id, stf_type=_stf_type, application_object=blender_object))
	elif(len(blender_armatures) > 1):
		context.report(STFReport("More than one Armature per mesh is not supported!", severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_id, stf_type=_stf_type, application_object=blender_object))
	else:
		ret["mesh"] = context.serialize_resource(blender_mesh, module_kind="data")

	material_slots = []
	for blender_slot in blender_object.material_slots:
		material_slots.append({
			"name": blender_slot.name,
			"material": context.serialize_resource(blender_slot.material, module_kind="data") if blender_slot.material else None,
		})
	ret["material_slots"] = material_slots

	blendshape_values = []
	if(blender_mesh.shape_keys):
		for blendshape in blender_mesh.shape_keys.key_blocks:
			blendshape_values.append(blendshape.value)
	ret["blendshape_values"] = blendshape_values

	return ret, str(uuid.uuid4())


class STF_Module_STF_Instance_Mesh(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["instance.mesh", "instance"]
	understood_application_types = [tuple]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object

	translate_property_to_stf_func = _translate_property_to_stf_func
	translate_property_to_blender_func: _translate_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Instance_Mesh
]


def register():
	pass

def unregister():
	pass
