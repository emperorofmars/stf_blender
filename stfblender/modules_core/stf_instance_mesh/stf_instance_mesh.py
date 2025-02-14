import bpy


from ....libstf.stf_export_context import STF_ResourceExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from ..stf_node.node_base import export_node_base, import_node_base
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.instance.mesh"


def _stf_import(context: STF_ResourceImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_resource = context.import_resource(json_resource["instance"]["mesh"])
	blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_resource)
	context.register_imported_resource(stf_id, blender_object)

	if(not blender_object or type(blender_object) is not bpy.types.Object):
		context.report(STFReport("Failed to import mesh: " + str(json_resource.get("instance", {}).get("mesh")), STFReportSeverity.Error, stf_id, _stf_type, parent_application_object))

	if("armature_instance" in json_resource["instance"]):
		armature_instance: bpy.types.Object = context.import_resource(json_resource["instance"]["armature_instance"])
		if(not armature_instance):
			context.report(STFReport("Invalid armature instance: " + str(json_resource["instance"]["armature_instance"]), STFReportSeverity.Error, stf_id, _stf_type, parent_application_object))
		else:
			modifier: bpy.types.ArmatureModifier = blender_object.modifiers.new("Armature", "ARMATURE")
			modifier.object = armature_instance

	# TODO handle materials, blendshape values

	return import_node_base(context, json_resource, stf_id, parent_application_object, blender_object)


def _can_handle_application_object_func(application_object: any) -> int:
	if(type(application_object) == bpy.types.Object and type(application_object.data) == bpy.types.Mesh):
		return 1000
	else:
		return -1

def _stf_export(context: STF_ResourceExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ret = {"type": _stf_type}
	ret, stf_id, context = export_node_base(context, blender_object, parent_application_object, ret)

	blender_object.update_from_editmode()
	blender_mesh: bpy.types.Mesh = blender_object.data

	ret_instance = {"type": _stf_type}
	ret["instance"] = ret_instance
	mesh_instance_context = STF_ResourceExportContext(context, ret_instance, blender_mesh)

	blender_armatures: list[bpy.types.ArmatureModifier] = []
	for _, modifier in blender_object.modifiers.items():
		if(type(modifier) is bpy.types.ArmatureModifier):
			blender_armatures.append(modifier)

	if(len(blender_armatures) == 1):
		if(blender_armatures[0].object.stf_id):
			# TODO check if the armature is in the export and within the same hierarchy, otherwise check if its in an instanced hierarchy

			# The armature has to be passed, because in Blenders datamodel the relationship between mesh and armature loose.
			ret_instance["mesh"] = mesh_instance_context.serialize_resource(blender_mesh, blender_armatures[0].object.data)
			ret_instance["armature_instance"] = mesh_instance_context.serialize_resource(blender_armatures[0].object)
		else:
			mesh_instance_context.report(STFReport("Invalid armature: " + str(blender_armatures[0].object), severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_id, stf_type=_stf_type, application_object=blender_object))
	elif(len(blender_armatures) > 1):
		mesh_instance_context.report(STFReport("More than one Armature per mesh is not supported!", severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_id, stf_type=_stf_type, application_object=blender_object))
	else:
		ret_instance["mesh"] = mesh_instance_context.serialize_resource(blender_mesh)

	material_slots = []
	for blender_slot in blender_object.material_slots:
		material_slots.append({
			"name": blender_slot.name,
			"material": mesh_instance_context.serialize_resource(blender_slot.material) if blender_slot.material else None,
		})
	ret_instance["material_slots"] = material_slots

	blendshape_values = []
	if(blender_mesh.shape_keys):
		for blendshape in blender_mesh.shape_keys.key_blocks:
			blendshape_values.append(blendshape.value)
	ret_instance["blendshape_values"] = blendshape_values

	return export_node_base(context, blender_object, parent_application_object, ret)


class STF_Module_STF_Instance_Mesh(STF_Module):
	stf_type = _stf_type
	stf_kind = "instance"
	like_types = ["instance.mesh", "instance"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	can_handle_application_object_func = _can_handle_application_object_func
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Instance_Mesh
]


def register():
	pass

def unregister():
	pass
