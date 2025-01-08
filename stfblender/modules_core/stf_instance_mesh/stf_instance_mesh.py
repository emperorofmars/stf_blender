import bpy

from ....libstf.stf_export_context import STF_RootExportContext
from ....libstf.stf_import_context import STF_RootImportContext
from ....libstf.stf_module import STF_ExportHook, STF_ImportHook
from ....libstf.stf_report import STF_Report_Severity, STFReport
from ...utils.component_utils import get_components_from_object
from ...utils.id_utils import ensure_stf_id
from ...utils.trs_utils import trs_to_blender_object


_stf_type = "stf.instance.mesh"


def _hook_can_handle_stf_object_func(json_resource: dict) -> tuple[bool, dict]:
	for _, component in json_resource.get("components", {}).items():
		# TODO also check 'likeness'
		if(component.get("type") == "stf.instance.mesh"):
			return (True, component)
	return (False, None)

def _stf_import(context: STF_RootImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	print("MESH: " + str(id) + " :: " + json_resource["name"])
	print(str(json_resource))

	blender_mesh = context.import_resource(json_resource["mesh"])
	# TODO handle materials, armatures, blendshape values

	if(not blender_mesh or type(blender_mesh) is not bpy.types.Mesh):
		context.report(STFReport("Failed to import mesh: " + str(json_resource.get("mesh")), STF_Report_Severity.Error, id, _stf_type, parent_application_object))

	blender_object: bpy.types.Object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_mesh)
	blender_object.stf_id = id

	trs_to_blender_object(json_resource["trs"], blender_object)

	for child_id in json_resource.get("children", []):
		child: bpy.types.Object = context.import_resource(child_id)
		if(child):
			child.parent_type = "OBJECT"
			child.parent = blender_object
		else:
			context.report(STFReport("Invalid Child: " + str(child_id), STF_Report_Severity.Error, id, _stf_type, blender_object))

	return blender_object


def _hook_can_handle_application_object_func(application_object: any) -> tuple[bool, any]:
	if(type(application_object.data) == bpy.types.Mesh):
		return (True, application_object.data)
	else:
		return (False, None)

def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	parent_blender_object: bpy.types.Object = parent_application_object

	blender_mesh: bpy.types.Mesh = application_object
	mesh_id = context.serialize_resource(blender_mesh)

	blender_armatures = []
	for _, modifier in parent_blender_object.modifiers.items():
		if(type(modifier) is bpy.types.ArmatureModifier):
			blender_armatures.append(modifier)

	armature_instance_id = None
	if(len(blender_armatures) == 1):
		armature_instance_id = context.serialize_resource(blender_mesh)
	elif(len(blender_armatures) > 1):
		context.report(STFReport("More than one Armature per mesh is not supported!", severity=STF_Report_Severity.FatalError, stf_id=parent_blender_object.stf_id, stf_type=_stf_type, application_object=parent_blender_object))

	material_slots = []
	for blender_slot in parent_blender_object.material_slots:
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
		"name": parent_blender_object.name,
		"mesh": mesh_id,
		"armature_instance": armature_instance_id,
		"material_slots": material_slots,
		"blendshape_values": blendshape_values
	}

	return ret, parent_blender_object.stf_id, context


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
