import bpy
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Handler_Animation, STF_Component_Ref, add_component, export_component_base, import_component_base, preserve_component_reference
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from ....stfblender_common.helpers import create_add_button, create_remove_button
from ....stfblender_common.blender_grr.stf_node_path_selector import draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf, node_path_selector_to_string, validate_node_path_selector
from .util.constraint_source import ConstraintSource


_stf_type = "stfexp.constraint.rotation"
_blender_property_name = "stfexp_constraint_rotation"


class STFEXP_Constraint_Rotation(STF_ComponentResourceBase):
	weight: bpy.props.FloatProperty(name="Constraint Weight", default=1.0, subtype="FACTOR", min=0, max=1) # type: ignore
	axes: bpy.props.BoolVectorProperty(name="Axes", default=(True, True, True), options=set(), size=3) # type: ignore
	sources: bpy.props.CollectionProperty(type=ConstraintSource, name="Sources") # type: ignore
	active_source_index: bpy.props.IntProperty() # type: ignore


class STFDrawAVAExpressionList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_stfexp_constraint_rotation_sources_list"

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: ConstraintSource, icon, active_data, active_propname, index): # pyright: ignore[reportIncompatibleMethodOverride]
		if(validate_node_path_selector(item.source)):
			layout.label(text=node_path_selector_to_string(item.source), icon="RIGHTARROW")
			layout.prop(item, "weight")
		else:
			layout.alert = True
			layout.label(text="No source selected!")


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Constraint_Rotation):
	layout.use_property_split = True

	layout.prop(component, "weight")
	row = layout.row(align=True, heading="Axes")
	row.prop(component, "axes", toggle=True, index=0, text="X")
	row.prop(component, "axes", toggle=True, index=1, text="Y")
	row.prop(component, "axes", toggle=True, index=2, text="Z")

	layout.separator(factor=1)

	create_add_button(layout, "bone" if type(context_resource) is bpy.types.Bone else "object", _blender_property_name, component.stf_id, "sources", text="Add Constraint Source")

	row = layout.row(align=True)
	row.template_list(STFDrawAVAExpressionList.bl_idname, "", component, "sources", component, "active_source_index")
	create_remove_button(row, "bone" if type(context_resource) is bpy.types.Bone else "object", _blender_property_name, component.stf_id, "sources", component.active_source_index)

	if(component.active_source_index < len(component.sources)):
		source = component.sources[component.active_source_index]
		col = layout.column(align=True)
		if(not validate_node_path_selector(source.source)):
			col.alert = True
		draw_node_path_selector(col, source.source, "Source")
		layout.prop(source, "weight")


"""Import export"""

def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any:
	component_ref, component = add_component(context_resource, _blender_property_name, stf_id, _stf_type) # pyright: ignore[reportAssignmentType]
	import_component_base(context, component, json_resource, _blender_property_name, context_resource)
	component: STFEXP_Constraint_Rotation = component

	component.weight = json_resource.get("weight", 1)
	component.axes = json_resource.get("axes", [True, True, True])

	_get_component = preserve_component_reference(component, _blender_property_name, context_resource)
	def _handle():
		component = _get_component()
		for json_source in json_resource.get("sources", []):
			source = component.sources.add()
			source.weight = json_source.get("weight")
			node_path_selector_from_stf(context, json_resource, json_source.get("source"), source.source)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return component


def _stf_export(context: STF_ExportContext, blender_resource: STFEXP_Constraint_Rotation, context_resource: Any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, blender_resource, _blender_property_name, context_resource)

	ret["weight"] = blender_resource.weight
	ret["axes"] = blender_resource.axes[:]

	sources = []
	ret["sources"] = sources

	_get_component = preserve_component_reference(blender_resource, _blender_property_name, context_resource)
	def _handle():
		component = _get_component()
		for source in component.sources:
			if(source_ret := node_path_selector_to_stf(context, source.source, ret)):
				sources.append({
					"source": source_ret,
					"weight": source.weight,
				})
	context.add_task(STF_TaskSteps.DEFAULT, _handle)

	return ret, blender_resource.stf_id


"""Bone instance handling"""

def _set_component_instance_standin(context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Constraint_Rotation, component_instance: STFEXP_Constraint_Rotation):
	component_instance.sources.clear()
	for source_original in component.sources:
		source = component_instance.sources.add()
		source.weight = source_original.weight
		source.source.target_object = context_resource
		source.source.target_bone = source_original.source.target_bone


def _export_component_instance(context: STF_ExportContext, component_ref: STF_Component_Ref, component_instance: STFEXP_Constraint_Rotation, context_resource: Any) -> dict:
	ret = {}

	ret["weight"] = component_instance.weight
	ret["axes"] = component_instance.axes[:]

	sources = []
	ret["sources"] = sources

	_get_component = preserve_component_reference(component_instance, _blender_property_name, context_resource)
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

def _import_component_instance(context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, standin_component: STFEXP_Constraint_Rotation, context_object: Any):
	_get_component = preserve_component_reference(standin_component, _blender_property_name, context_object)

	standin_component.weight = json_resource.get("weight", 1)
	standin_component.axes = json_resource.get("axes", [True, True, True])

	def _handle():
		component = _get_component()
		for json_source in json_resource.get("sources", []):
			source = component.sources.add()
			source.weight = json_source.get("weight")
			node_path_selector_from_stf(context, json_resource, json_source.get("source"), source.source)
	context.add_task(STF_TaskSteps.DEFAULT, _handle)


"""Animation"""

def _export_blender_animation(context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["enabled"])
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].weight", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["weight"])
	if(match := re.search(r"^" + _blender_property_name + r"\[(?P<component_index>[\d]+)\].sources\[(?P<source_index>[\d]+)\].weight", blender_property_path)):
		if(component_path := get_component_stf_path_from_collection(blender_resource, _blender_property_name, int(match.groupdict()["component_index"]))):
			return STFPropertyPathPart(component_path + ["sources", int(match.groupdict()["source_index"]), "weight"])
	return None


def _import_stf_animation_property_path_func(context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
	blender_resource = context.get_imported_resource(stf_property_path[0])
	component_index = get_component_index(blender_resource, _blender_property_name, blender_resource.stf_id)
	if(component_index is not None):
		match(stf_property_path[1]):
			case "enabled":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].enabled")
			case "weight":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].weight")
			case "sources":
				return BlenderPropertyPathPart("OBJECT", _blender_property_name + "[" + str(component_index) + "].sources[" + str(stf_property_path[2]) + "].weight")
	return None


"""Handler definition"""

class Handler_STFEXP_Constraint_Rotation(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""A rigging behaviour that applies rotation from its sources onto itself"""
	stf_type = _stf_type
	stf_category = STF_Category.COMPONENT
	like_types = ["constraint.rotation", "constraint"]
	understood_blender_types = [STFEXP_Constraint_Rotation]
	import_resource = _stf_import
	export_resource = _stf_export

	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [_blender_property_name]
	export_blender_animation = _export_blender_animation
	import_stf_animation_property_path_func = _import_stf_animation_property_path_func

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw = _draw_component

	draw_instance = _draw_component # pyright: ignore[reportAssignmentType]
	update_component_instance = _set_component_instance_standin

	export_component_instance = _export_component_instance # pyright: ignore[reportAssignmentType]
	import_component_instance = _import_component_instance # pyright: ignore[reportAssignmentType]

	pretty_name_template = "Rotation Constraint"


register_stf_handlers = [
	Handler_STFEXP_Constraint_Rotation
]


def register():
	setattr(bpy.types.Object, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Rotation, options=set()))
	setattr(bpy.types.Bone, _blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Rotation, options=set()))

def unregister():
	if hasattr(bpy.types.Object, _blender_property_name):
		delattr(bpy.types.Object, _blender_property_name)
	if hasattr(bpy.types.Bone, _blender_property_name):
		delattr(bpy.types.Bone, _blender_property_name)
