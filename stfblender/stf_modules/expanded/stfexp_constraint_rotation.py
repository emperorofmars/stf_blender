import re
import bpy
from typing import Callable

from ...base.stf_task_steps import STF_TaskSteps
from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ...utils.animation_conversion_utils import get_component_stf_path, get_component_stf_path_from_collection
from ...base.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf, node_path_selector_to_string, validate_node_path_selector
from ...utils.helpers import create_add_button, create_remove_button


_stf_type = "stfexp.constraint.rotation"
_blender_property_name = "stfexp_constraint_rotation"


class RotationConstraintSource(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5, subtype="FACTOR", soft_min=0, soft_max=1) # type: ignore
	source: bpy.props.PointerProperty(name="Source", type=NodePathSelector) # type: ignore


class STFEXP_Constraint_Rotation(STF_BlenderComponentBase):
	sources: bpy.props.CollectionProperty(type=RotationConstraintSource, name="Sources") # type: ignore
	active_source_index: bpy.props.IntProperty() # type: ignore


class STFDrawAVAExpressionList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stfexp_constraint_rotation_sources_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: RotationConstraintSource, icon, active_data, active_propname, index):
		if(validate_node_path_selector(item.source)):
			layout.label(text=node_path_selector_to_string(item.source), icon="RIGHTARROW")
			layout.prop(item, "weight")
		else:
			layout.alert = True
			layout.label(text="No source selected!")


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Rotation):
	layout.use_property_split = True

	create_add_button(layout, "bone" if type(context_object) == bpy.types.Bone else "object", _blender_property_name, component.stf_id, "sources", text="Add Constraint Source")

	row = layout.row(align=True)
	row.template_list(STFDrawAVAExpressionList.bl_idname, "", component, "sources", component, "active_source_index")
	create_remove_button(row, "bone" if type(context_object) == bpy.types.Bone else "object", _blender_property_name, component.stf_id, "sources", component.active_source_index)

	if(component.active_source_index < len(component.sources)):
		source = component.sources[component.active_source_index]
		col = layout.column(align=True)
		if(not validate_node_path_selector(source.source)):
			col.alert = True
		draw_node_path_selector(col, source.source, "Source")
		layout.prop(source, "weight")

	layout.separator(factor=1)
	total_weight = 0
	for s in component.sources:
		total_weight += s.weight
	layout.label(text="Total Weight: {:10.2f}".format(total_weight))


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, context_object)
	component: STFEXP_Constraint_Rotation = component

	_get_component = preserve_component_reference(component, context_object)
	def _handle():
		component = _get_component()
		for json_source in json_resource.get("sources", []):
			source = component.sources.add()
			source.weight = json_source.get("weight")
			node_path_selector_from_stf(context, json_resource, json_source.get("source"), source.source)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Constraint_Rotation, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)
	sources = []
	ret["sources"] = sources

	_get_component = preserve_component_reference(component, context_object)
	def _handle():
		component = _get_component()
		for source in component.sources:
			if(source_ret := node_path_selector_to_stf(context, source.source, ret)):
				sources.append({
					"source": source_ret,
					"weight": source.weight,
				})
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return ret, component.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Rotation, standin_component: STFEXP_Constraint_Rotation):
	for source_original in component.sources:
		source = standin_component.sources.add()
		source.weight = source_original.weight
		source.source.target_object = source_original.source.target_object
		source.source.target_bone = source_original.source.target_bone


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Rotation, context_object: any) -> dict:
	ret = {}
	sources = []
	ret["sources"] = sources
	_get_component = preserve_component_reference(standin_component, context_object)
	def _handle():
		component = _get_component()
		for source in component.sources:
			if(source_ret := node_path_selector_to_stf(context, source.source, ret)):
				sources.append({
					"source": source_ret,
					"weight": source.weight,
				})
	context.add_task(STF_TaskSteps.DEFAULT, _handle)
	return ret

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Rotation, context_object: any):
	_get_component = preserve_component_reference(standin_component, context_object)
	def _handle():
		component = _get_component()
		for json_source in json_resource.get("sources", []):
			source = component.sources.add()
			source.weight = json_source.get("weight")
			node_path_selector_from_stf(context, json_resource, json_source.get("source"), source.source)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> tuple[list[str], Callable[[int, any], any], list[int]]:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].sources\[(?P<source_index>[\d]+)\].weight", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return component_path + ["sources", int(match.groupdict()["source_index"]), "weight"], None, None
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return component_path + ["enabled"], None, None
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> tuple[any, int, any, any, list[int], Callable[[list[float]], list[float]]]:
	blender_object = context.get_imported_resource(stf_path[0])
	# let component_index
	for component_index, component in enumerate(getattr(application_object, _blender_property_name)):
		if(component.stf_id == blender_object.stf_id):
			break
	else:
		return None
	match(stf_path[1]):
		case "sources":
			return None, 0, "OBJECT", _blender_property_name + "[" + str(component_index) + "].sources[" + str(stf_path[2]) + "].weight", 0, None
		case "enabled":
			return None, 0, "OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled", 0, None
	return None


"""Module definition"""

class STF_Module_STFEXP_Constraint_Rotation(STF_BlenderComponentModule):
	"""A rigging behaviour that applies rotation from its sources onto itself"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["constraint.rotation", "constraint"]
	understood_application_types = [STFEXP_Constraint_Rotation]
	import_func = _stf_import
	export_func = _stf_export

	understood_application_property_path_types = [bpy.types.Object]
	understood_application_property_path_parts = [_blender_property_name]
	resolve_property_path_to_stf_func = _resolve_property_path_to_stf_func
	resolve_stf_property_to_blender_func = _resolve_stf_property_to_blender_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component

	draw_component_instance_func = _draw_component
	set_component_instance_standin_func = _set_component_instance_standin

	serialize_component_instance_standin_func = _serialize_component_instance_standin_func
	parse_component_instance_standin_func = _parse_component_instance_standin_func


register_stf_modules = [
	STF_Module_STFEXP_Constraint_Rotation
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Rotation, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Rotation, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
