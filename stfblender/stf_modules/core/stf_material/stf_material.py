import bpy

from .stf_material_definition import STF_Material_Property, STF_Material_Value_Module_Base
from .material_value_modules import blender_material_value_modules
from .stf_material_operators import add_property, add_value_to_property
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....base.stf_module import STF_Module
from ....utils.component_utils import get_components_from_object
from ....utils.id_utils import ensure_stf_id
from ....utils.boilerplate import boilerplate_register, boilerplate_unregister
from .convert_blender_material_to_stf import blender_material_to_stf
from .convert_stf_material_to_blender import stf_material_to_blender
from .stf_material_property_conversion import stf_material_resolve_property_path_to_stf_func, stf_material_resolve_stf_property_to_blender_func


_stf_type = "stf.material"


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	blender_material = bpy.data.materials.new(json_resource.get("name", "STF Material"))
	blender_material.stf_info.stf_id = stf_id
	if(json_resource.get("name")):
		blender_material.stf_info.stf_name = json_resource["name"]
		blender_material.stf_info.stf_name_source_of_truth = True
	blender_material.stf_info.stf_is_source_of_truth = True
	context.register_imported_resource(stf_id, blender_material)

	for style_hint in json_resource.get("style_hints", []):
		hint = blender_material.stf_material.style_hints.add()
		hint.value = style_hint

	for stf_target, stf_shaders in blender_material.get("shader_targets", {}).items():
		shader_target = blender_material.stf_material.shader_targets.add()
		shader_target.target = stf_target
		for stf_shader in stf_shaders:
			shader = shader_target.shaders.add()
			shader.value = stf_shader

	for property_type, stf_property in json_resource.get("properties", {}).items():
		for material_value_module in blender_material_value_modules:
			material_value_module: STF_Material_Value_Module_Base = material_value_module
			if(material_value_module.value_type == stf_property.get("type")):
				prop, value_ref, value = add_property(blender_material, property_type, material_value_module)
				stf_values = stf_property.get("values")
				prop.multi_value = True
				if(len(stf_values) > 0):
					material_value_module.value_import_func(context, blender_material, stf_values[0], value)
					if(len(stf_values) > 1):
						for stf_value in stf_values[1:]:
							value_ref, value = add_value_to_property(blender_material, len(blender_material.stf_material.properties) - 1)
							material_value_module.value_import_func(context, blender_material, stf_value, value)
				else:
					pass # TODO report fail
				break

	stf_material_to_blender(blender_material)

	return blender_material


def _stf_export(context: STF_ExportContext, application_object: any, context_object: any) -> tuple[dict, str]:
	blender_material: bpy.types.Material = application_object
	ensure_stf_id(context, blender_material)

	ret = {
		"type": _stf_type,
		"name": blender_material.stf_info.stf_name if blender_material.stf_info.stf_name_source_of_truth else blender_material.name,
		"properties": {},
	}

	if(not blender_material.stf_material.stf_is_source_of_truth):
		blender_material_to_stf(blender_material)

	ret["style_hints"] = []
	for style_hint in blender_material.stf_material.style_hints:
		ret["style_hints"].append(style_hint.value)

	ret["shader_targets"] = {}
	for target in blender_material.stf_material.shader_targets:
		ret["shader_targets"][target.target] = []
		for shader in target.shaders:
			ret["shader_targets"][target.target].append(shader.value)


	for property in blender_material.stf_material.properties:
		property: STF_Material_Property = property
		json_prop = {"type": property.value_type}

		values = []
		for value_ref in property.values:
			for mat_module in blender_material_value_modules:
				if(mat_module.property_name == property.value_property_name):
					for property_value in getattr(blender_material, property.value_property_name):
						if(property_value.value_id == value_ref.value_id):
							# TODO check if export succeeded and warn if not
							values.append(mat_module.value_export_func(context, blender_material, property_value))
							break

		json_prop["values"] = values

		ret["properties"][property.property_type] = json_prop

	return ret, blender_material.stf_info.stf_id


class STF_Module_STF_Material(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["material"]
	understood_application_types = [bpy.types.Material]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = ["stf_material_value_"]
	resolve_property_path_to_stf_func = stf_material_resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = stf_material_resolve_stf_property_to_blender_func


register_stf_modules = [
	STF_Module_STF_Material
]


def register():
	boilerplate_register(bpy.types.Material, "data")

def unregister():
	boilerplate_unregister(bpy.types.Material, "data")
