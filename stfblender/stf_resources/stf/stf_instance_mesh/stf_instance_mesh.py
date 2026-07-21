import bpy
from typing import Any

from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Handler_BlenderNative, STF_Info, BlenderPropertyPathPart, STF_Handler_Animation, STFPropertyPathPart, STFReportSeverity, STFReport, STF_Category, ensure_stf_id
from .stf_instance_mesh_data import STF_Instance_Mesh
from .stf_instance_mesh_ui import STFSetMeshInstanceIDOperator, draw_instance_mesh_ui
from .stf_instance_mesh_util import set_instance_blendshapes


_stf_type = "stf.instance.mesh"


class Handler_STF_Instance_Mesh(STF_Handler_BlenderNative, STF_Handler_Animation):
	stf_type = _stf_type
	stf_category = STF_Category.INSTANCE
	like_types = ["instance.mesh", "instance"]
	understood_blender_types = [tuple]

	operator_set_stf_id = STFSetMeshInstanceIDOperator.bl_idname
	draw = draw_instance_mesh_ui

	get_stf_prop_holder = lambda blender_resource: blender_resource[0].stf_instance
	@staticmethod
	def get_stf_prop_holder(blender_resource: Any) -> STF_Info:
		return blender_resource[0].stf_instance

	@staticmethod
	def import_resource(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		blender_resource = context.import_resource(json_resource, json_resource["mesh"], stf_category=STF_Category.DATA)
		blender_object = bpy.data.objects.new(json_resource.get("name", "STF Node"), blender_resource)
		blender_object.stf_instance.stf_id = stf_id
		if(json_resource.get("name")):
			blender_object.stf_instance.stf_name = json_resource["name"]
		context.register_imported_resource(stf_id, (blender_object, blender_resource))

		if(not blender_object or type(blender_object) is not bpy.types.Object):
			context.report(STFReport("Failed to import mesh: " + str(json_resource.get("instance", {}).get("mesh")), STFReportSeverity.Error, stf_id, _stf_type, context_resource))

		if("armature_instance" in json_resource):
			armature_instance: bpy.types.Object | None = context.import_resource(json_resource, json_resource["armature_instance"], stf_category=STF_Category.NODE)
			if(not armature_instance):
				context.report(STFReport("Invalid armature instance: " + str(json_resource["armature_instance"]), STFReportSeverity.Error, stf_id, _stf_type, context_resource))
			else:
				modifier: bpy.types.ArmatureModifier = blender_object.modifiers.new("Armature", "ARMATURE")  # pyright: ignore[reportAssignmentType]
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
					instance_blendshape.index_on_mesh = index

		if("materials" in json_resource):
			for material_index, material_id in enumerate(json_resource["materials"]):
				if(material_id and len(blender_object.material_slots) > material_index):
					if(material := context.import_resource(json_resource, material_id, stf_category=STF_Category.DATA)):
						blender_object.material_slots[material_index].link = "OBJECT"
						blender_object.material_slots[material_index].material = material

		return blender_object

	@staticmethod
	def export_resource(context: STF_ExportContext, application_object: Any, context_object: bpy.types.Collection) -> tuple[dict, str] | STFReport:
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
				return STFReport("Armature sits outside the exported asset", severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_info.stf_id, stf_type=_stf_type, application_object=blender_object)
			# The armature has to be passed, because in Blenders datamodel, the relationship between mesh and armature is loose.
			ret["mesh"] = context.serialize_resource(ret, blender_mesh, blender_armatures[0].object.data, stf_category=STF_Category.DATA)
			ret["armature_instance"] = context.serialize_resource(ret, blender_armatures[0].object, stf_category=STF_Category.NODE)
		elif(len(blender_armatures) > 1):
			return STFReport("More than one Armature per mesh is not supported!", severity=STFReportSeverity.FatalError, stf_id=blender_object.stf_info.stf_id, stf_type=_stf_type, application_object=blender_object)
		else:
			ret["mesh"] = context.serialize_resource(ret, blender_mesh, stf_category=STF_Category.DATA)

		material_slots = []
		for material_slot in blender_object.material_slots:
			if(material_slot.material and material_slot.link == "OBJECT"):
				material_slots.append(context.serialize_resource(ret, material_slot.material, stf_category=STF_Category.DATA))
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

	@staticmethod
	def can_handle_blender_resource(blender_resource: Any) -> int:
		if(type(blender_resource) is tuple and type(blender_resource[0]) is bpy.types.Object and type(blender_resource[1]) is bpy.types.Mesh):
			return 1000
		else:
			return -1

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = ["key_blocks"]

	@staticmethod
	def export_blender_animation(context: STF_ExportContext, blender_object: Any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart | None:
		import re
		match = re.search(r"^key_blocks\[\"(?P<blendshape_name>[\w. -:,]+)\"\].value", data_path)
		if(match and "blendshape_name" in match.groupdict()):
			return STFPropertyPathPart([blender_object.stf_info.stf_id, "instance", "blendshape", match.groupdict()["blendshape_name"], "value"])
		return None

	@staticmethod
	def import_stf_animation_property_path_func(context: STF_ImportContext, stf_path: list[str], blender_object: bpy.types.Object) -> BlenderPropertyPathPart | None:
		if(len(stf_path) == 4 and stf_path[1] == "blendshape" and stf_path[3] == "value"):
			return BlenderPropertyPathPart("KEY", "key_blocks[\"" + stf_path[2] + "\"].value")
		elif(len(stf_path) >= 5 and stf_path[1] == "material"):
			material_index = int(stf_path[2])
			if(len(blender_object.material_slots) <= material_index or not blender_object.material_slots[material_index].material):
				return None

			return BlenderPropertyPathPart(slot_link_target = blender_object, slot_link_property_index = material_index) + context.resolve_stf_property_path([blender_object.material_slots[material_index].material.stf_info.stf_id] + stf_path[2:], blender_object)
		return None


def register():
	bpy.types.Object.stf_instance_mesh = bpy.props.PointerProperty(type=STF_Instance_Mesh, options=set()) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stf_instance_mesh"):
		del bpy.types.Object.stf_instance_mesh
