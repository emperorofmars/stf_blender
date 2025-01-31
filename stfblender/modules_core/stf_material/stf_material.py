import bpy


from ....libstf.stf_export_context import STF_ResourceExportContext, STF_RootExportContext
from ....libstf.stf_import_context import STF_ResourceImportContext, STF_RootImportContext
from ....libstf.stf_module import STF_Module
from ....libstf.stf_report import STFReportSeverity, STFReport
from .stf_material_definition import STF_Material_Definition, STF_Material_Property, STF_Material_Value_Ref
from .blender_material_to_stf import blender_material_to_stf
from ...utils.component_utils import STF_Component_Ref, get_components_from_object
from ...utils.id_utils import ensure_stf_id
from .material_value_modules import blender_material_value_modules


_stf_type = "stf.material"


def _stf_import(context: STF_RootImportContext, json_resource: dict, stf_id: str, parent_application_object: any) -> tuple[any, any]:
	blender_material = bpy.data.materials.new(json_resource.get("name", "STF Material"))
	blender_material.stf_id = stf_id
	if(json_resource.get("name")):
		blender_material.stf_name = json_resource["name"]
		blender_material.stf_name_source_of_truth = True
	blender_material.stf_is_source_of_truth = True
	context.register_imported_resource(stf_id, blender_material)

	material_context = STF_ResourceImportContext(context, json_resource, blender_material)

	return blender_material, material_context


def _stf_export(context: STF_RootExportContext, application_object: any, parent_application_object: any) -> tuple[dict, str, any]:
	blender_material: bpy.types.Material = application_object
	ensure_stf_id(context, blender_material)

	ret = {
		"type": _stf_type,
		"name": blender_material.stf_name if blender_material.stf_name_source_of_truth else blender_material.name,
		"properties": {},
	}
	material_context = STF_ResourceExportContext(context, ret, blender_material)

	if(not blender_material.stf_is_source_of_truth):
		blender_material_to_stf(blender_material)


	ret["style_hints"] = []
	for style_hint in blender_material.stf_material.style_hints:
		ret["style_hints"].append(style_hint.value)

	ret["shader_targets"] = {}
	for target in blender_material.stf_material.shader_targets:
		ret["shader_targets"][target.target] = []
		for shader in target.shaders:
			ret["shader_targets"][target.target].append(shader.value)


	for property in blender_material.stf_material_properties:
		property: STF_Material_Property = property
		json_prop = {"value_type": property.value_type}

		values = []
		for value_ref in property.values:
			for mat_module in blender_material_value_modules:
				if(mat_module.property_name == property.value_property_name):
					for property_value in getattr(blender_material, property.value_property_name):
						if(property_value.value_id == value_ref.value_id):
							values.append(mat_module.value_export_func(material_context, blender_material, getattr(blender_material, property.value_property_name)[0]))
							break

		if(property.multi_value):
			json_prop["values"] = values
		elif(len(values) > 0):
			json_prop["value"] = values[0]

		ret["properties"][property.property_type] = json_prop

	return ret, blender_material.stf_id, material_context


class STF_Module_STF_Material(STF_Module):
	stf_type = _stf_type
	stf_kind = "data"
	like_types = ["material"]
	understood_application_types = [bpy.types.Material]
	import_func = _stf_import
	export_func = _stf_export
	get_components_func = get_components_from_object


register_stf_modules = [
	STF_Module_STF_Material
]


def register():
	bpy.types.Material.stf_id = bpy.props.StringProperty(name="ID") # type: ignore
	bpy.types.Material.stf_name = bpy.props.StringProperty(name="Name") # type: ignore
	bpy.types.Material.stf_name_source_of_truth = bpy.props.BoolProperty(name="STF Name Is Source Of Truth") # type: ignore
	bpy.types.Material.stf_components = bpy.props.CollectionProperty(type=STF_Component_Ref, name="Components") # type: ignore
	bpy.types.Material.stf_active_component_index = bpy.props.IntProperty()

def unregister():
	if hasattr(bpy.types.Material, "stf_id"):
		del bpy.types.Material.stf_id
	if hasattr(bpy.types.Material, "stf_name"):
		del bpy.types.Material.stf_name
	if hasattr(bpy.types.Material, "stf_name_source_of_truth"):
		del bpy.types.Material.stf_name_source_of_truth
	if hasattr(bpy.types.Material, "stf_components"):
		del bpy.types.Material.stf_components
	if hasattr(bpy.types.Material, "stf_active_component_index"):
		del bpy.types.Material.stf_active_component_index
