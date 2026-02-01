import re
import bpy

from ...base.stf_task_steps import STF_TaskSteps
from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base, preserve_component_reference
from ...utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from ...base.blender_grr.stf_node_path_selector import draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf, node_path_selector_to_string, validate_node_path_selector
from ...utils.helpers import create_add_button, create_remove_button
from ...base.property_path_part import BlenderPropertyPathPart, STFPropertyPathPart
from .util.constraint_source import ConstraintSource


_stf_type = "stfexp.constraint.parent"
_blender_property_name = "stfexp_constraint_parent"


class STFEXP_Constraint_Parent(STF_BlenderComponentBase):
	weight: bpy.props.FloatProperty(name="Constraint Weight", default=1.0, subtype="FACTOR", min=0, max=1) # type: ignore
	translation_axes: bpy.props.BoolVectorProperty(name="Translation Axes", default=(True, True, True), options=set(), size=3) # type: ignore
	rotation_axes: bpy.props.BoolVectorProperty(name="Rotation Axes", default=(True, True, True), options=set(), size=3) # type: ignore
	sources: bpy.props.CollectionProperty(type=ConstraintSource, name="Sources") # type: ignore
	active_source_index: bpy.props.IntProperty() # type: ignore


class STFDrawAVAExpressionList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stfexp_constraint_parent_sources_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: ConstraintSource, icon, active_data, active_propname, index):
		if(validate_node_path_selector(item.source)):
			layout.label(text=node_path_selector_to_string(item.source), icon="RIGHTARROW")
			layout.prop(item, "weight")
		else:
			layout.alert = True
			layout.label(text="No source selected!")


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Parent):
	layout.use_property_split = True

	layout.prop(component, "weight")
	row = layout.row(align=True, heading="Translation Axes")
	row.prop(component, "translation_axes", toggle=True, index=0, text="X")
	row.prop(component, "translation_axes", toggle=True, index=1, text="Y")
	row.prop(component, "translation_axes", toggle=True, index=2, text="Z")
	row = layout.row(align=True, heading="Rotation Axes")
	row.prop(component, "rotation_axes", toggle=True, index=0, text="X")
	row.prop(component, "rotation_axes", toggle=True, index=1, text="Y")
	row.prop(component, "rotation_axes", toggle=True, index=2, text="Z")

	layout.separator(factor=1)

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


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	component: STFEXP_Constraint_Parent = component

	component.weight = json_resource.get("weight", 1)
	component.translation_axes = json_resource.get("translation_axes", [True, True, True])
	component.rotation_axes = json_resource.get("rotation_axes", [True, True, True])

	_get_component = preserve_component_reference(component, _blender_property_name, context_object)
	def _handle():
		component = _get_component()
		for json_source in json_resource.get("sources", []):
			source = component.sources.add()
			source.weight = json_source.get("weight")
			node_path_selector_from_stf(context, json_resource, json_source.get("source"), source.source)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_Constraint_Parent, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)

	ret["weight"] = component.weight
	ret["translation_axes"] = component.translation_axes[:]
	ret["rotation_axes"] = component.rotation_axes[:]

	sources = []
	ret["sources"] = sources

	_get_component = preserve_component_reference(component, _blender_property_name, context_object)
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

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: STFEXP_Constraint_Parent, standin_component: STFEXP_Constraint_Parent):
	for source_original in component.sources:
		source = standin_component.sources.add()
		source.weight = source_original.weight
		source.source.target_object = source_original.source.target_object
		source.source.target_bone = source_original.source.target_bone


def _serialize_component_instance_standin_func(context: STF_ExportContext, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Parent, context_object: any) -> dict:
	ret = {}

	ret["weight"] = standin_component.weight
	ret["translation_axes"] = standin_component.translation_axes[:]
	ret["rotation_axes"] = standin_component.rotation_axes[:]

	sources = []
	ret["sources"] = sources

	_get_component = preserve_component_reference(standin_component, _blender_property_name, context_object)
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

def _parse_component_instance_standin_func(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Parent, context_object: any):
	_get_component = preserve_component_reference(standin_component, _blender_property_name, context_object)

	standin_component.weight = json_resource.get("weight", 1)
	standin_component.translation_axes = json_resource.get("translation_axes", [True, True, True])
	standin_component.rotation_axes = json_resource.get("rotation_axes", [True, True, True])

	def _handle():
		component = _get_component()
		for json_source in json_resource.get("sources", []):
			source = component.sources.add()
			source.weight = json_source.get("weight")
			node_path_selector_from_stf(context, json_resource, json_source.get("source"), source.source)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)


"""Animation"""

def _resolve_property_path_to_stf_func(context: STF_ExportContext, application_object: any, application_object_property_index: int, data_path: str) -> STFPropertyPathPart:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].weight", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["weight"])
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].sources\[(?P<source_index>[\d]+)\].weight", data_path)):
		if(component_path := get_component_stf_path_from_collection(application_object, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["sources", int(match.groupdict()["source_index"]), "weight"])
	return None


def _resolve_stf_property_to_blender_func(context: STF_ImportContext, stf_path: list[str], application_object: any) -> BlenderPropertyPathPart:
	blender_object = context.get_imported_resource(stf_path[0])
	if(component_index := get_component_index(application_object, _blender_property_name, blender_object.stf_id)):
		match(stf_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
			case "weight":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].weight")
			case "sources":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].sources[" + str(stf_path[2]) + "].weight")
	return None


"""Module definition"""

class STF_Module_STFEXP_Constraint_Parent(STF_BlenderComponentModule):
	"""A rigging behaviour that parents itself to its sources"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["constraint.parent", "constraint"]
	understood_application_types = [STFEXP_Constraint_Parent]
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
	STF_Module_STFEXP_Constraint_Parent
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Parent, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Parent, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
