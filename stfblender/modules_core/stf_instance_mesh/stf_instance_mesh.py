import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_ExportHook, STF_ImportHook
from ....libstf.stf_report import STF_Report_Severity, STFReport
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id


_stf_type = "stf.instance.mesh"


def _hook_can_handle_stf_object_func(json_resource: dict) -> bool:
	for _, component in json_resource.get("components", {}):
		# TODO also chack 'likeness'
		if(component.get("type") == "stf.mesh"):
			print("TRUE\n")
			return True
	return False

def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any = None) -> any:
	print("\nHOOK\n")


def _hook_can_handle_application_object_func(application_object: any) -> bool:
	return type(application_object.data) == bpy.types.Mesh

def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any = None) -> tuple[dict, str, any]:
	blender_object: bpy.types.Object = application_object
	ensure_stf_id(blender_object)

	print(application_object)
	print(parent_application_object)

	blender_mesh: bpy.types.Mesh = application_object.data

	mesh_id = context.serialize_resource(blender_mesh)

	blender_armatures = []
	for _, modifier in blender_object.modifiers.items():
		if(type(modifier) is bpy.types.ArmatureModifier):
			blender_armatures.append(modifier)

	armature_instance_id = None
	if(len(blender_armatures) == 1):
		armature_instance_id = context.serialize_resource(blender_mesh)
	elif(len(blender_armatures) > 1):
		context.report(STFReport("More than one Armature per mesh is not supported!", severity=STF_Report_Severity.FatalError, stf_id=blender_object.stf_id, stf_type=_stf_type, application_object=blender_object))

	material_slots = []
	for blender_slot in blender_object.material_slots:
		material_slots.append({
			"name": blender_slot.name,
			"material": context.serialize_resource(blender_slot.material) if blender_slot.material else None,
		})

	blendshape_values = []
	if(blender_mesh.shape_keys):
		for blendshape in blender_mesh.shape_keys.key_blocks:
			blendshape_values.append(blendshape.value)

	ret = {
		"type": _stf_type,
		"name": blender_object.name,
		"mesh": mesh_id,
		"armature_instance": armature_instance_id,
		"material_slots": material_slots,
		"blendshape_values": blendshape_values
	}

	return ret, blender_object.stf_id, context


class STF_Module_STF_Instance_Mesh(STF_ImportHook, STF_ExportHook):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["instance.mesh", "instance"]
	understood_application_types = [bpy.types.Object]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object

	hook_target_stf_type = "stf.node.spatial"
	hook_can_handle_stf_object_func = _hook_can_handle_stf_object_func

	hook_target_application_types = [bpy.types.Object]
	hook_can_handle_application_object_func = _hook_can_handle_application_object_func


register_stf_modules = [
	STF_Module_STF_Instance_Mesh
]


def register():
	pass

def unregister():
	pass
