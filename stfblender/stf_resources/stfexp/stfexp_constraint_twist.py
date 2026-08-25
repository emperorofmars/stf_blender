import bpy
import re
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, BlenderPropertyPathPart, STFPropertyPathPart, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_BoneComponent, STF_Handler_Animation, STF_Component_Ref, STF_ComponentBoneInstanceRef, STFReport, add_component, export_component_base, import_component_base, preserve_component_reference
from ....stfblender_common.utils.animation_conversion_utils import get_component_index, get_component_stf_path_from_collection
from ....stfblender_common.blender_grr.stf_node_path_selector import NodePathSelector, draw_node_path_selector, node_path_selector_from_stf, node_path_selector_to_stf, validate_node_path_selector


class STFEXP_Constraint_Twist(STF_ComponentResourceBase):
	weight: bpy.props.FloatProperty(name="Weight", default=0.5)
	source: bpy.props.PointerProperty(name="Source", type=NodePathSelector)


class Handler_STFEXP_Constraint_Twist(STF_Handler_BoneComponent, STF_Handler_Animation):
	"""A rigging behaviour which copies an amount of the Y-axis rotation from the source object/bone. If no source is selected, the parent of the parent will be assumed"""
	stf_type = "stfexp.constraint.twist"
	blender_property_name = "stfexp_constraint_twist"
	stf_category = STF_Category.COMPONENT
	like_types = ["constraint.rotation", "constraint"]
	understood_blender_types = [STFEXP_Constraint_Twist]
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	pretty_name_template = "Twist Constraint"

	@classmethod
	def _draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref | STF_ComponentBoneInstanceRef, context_resource: Any, component: STFEXP_Constraint_Twist, default_parent: bpy.types.Bone | bpy.types.Object | None):
		layout.use_property_split = True
		layout.prop(component, "weight")
		if(not validate_node_path_selector(component.source)):
			if(default_parent):
				layout.label(text="Default target if no valid Source is selected: " + default_parent.name)
			else:
				layout.label(text="If no Source is selected, the parent of the parent will be assumed.", icon="INFO")
		col = layout.column(align=True)
		col.use_property_split = True
		draw_node_path_selector(col, component.source, "Source")

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Constraint_Twist):
		default_parent = None
		if(type(context_resource) is bpy.types.Bone and context_resource.parent and context_resource.parent.parent):
			default_parent = context_resource.parent.parent
		cls._draw(layout, context, component_ref, context_resource, component, default_parent)

	@classmethod
	def draw_instance(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_ComponentBoneInstanceRef, context_resource: Any, component: STFEXP_Constraint_Twist) -> None:
		default_parent = None
		if(component_ref.id_data.data.bones[component_ref.bone].parent and component_ref.id_data.data.bones[component_ref.bone].parent.parent):
			default_parent = component_ref.id_data.data.bones[component_ref.bone].parent.parent
		cls._draw(layout, context, component_ref, context_resource, component, default_parent)

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		component.weight = json_resource.get("weight")

		if("source" in json_resource):
			_get_component = preserve_component_reference(component, cls.blender_property_name, context_resource)
			def _handle():
				component = _get_component()
				node_path_selector_from_stf(context, json_resource, json_resource["source"], component.source)
			context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, blender_resource: STFEXP_Constraint_Twist, context_resource: Any) -> tuple[dict, str]:
		ret = export_component_base(context, cls.stf_type, blender_resource, cls.blender_property_name, context_resource)
		ret["weight"] = blender_resource.weight

		_get_component = preserve_component_reference(blender_resource, cls.blender_property_name, context_resource)
		def _handle():
			component = _get_component()
			if(source_ret := node_path_selector_to_stf(context, component.source, ret)):
				ret["source"] = source_ret
		context.add_task(STF_TaskSteps.DEFAULT, _handle)

		return ret, blender_resource.stf_id


	understood_blender_animation_types = [bpy.types.Object]
	understood_blender_animation_data_paths = [blender_property_name]

	@classmethod
	def export_blender_animation(cls, context: STF_ExportContext, blender_resource: Any, property_index: int, blender_property_path: str) -> STFPropertyPathPart | None:
		if(match := re.search(r"^" + cls.blender_property_name + r"\[(?P<component_index>[\d]+)\].weight", blender_property_path)):
			if(component_path := get_component_stf_path_from_collection(blender_resource, cls.blender_property_name, int(match.groupdict()["component_index"]))):
				return STFPropertyPathPart(component_path + ["weight"])
		if(match := re.search(r"^" + cls.blender_property_name + r"\[(?P<component_index>[\d]+)\].enabled", blender_property_path)):
			if(component_path := get_component_stf_path_from_collection(blender_resource, cls.blender_property_name, int(match.groupdict()["component_index"]))):
				return STFPropertyPathPart(component_path + ["enabled"])
		return None

	@classmethod
	def import_stf_animation(cls, context: STF_ImportContext, stf_property_path: list[str], blender_resource: Any) -> BlenderPropertyPathPart | None:
		blender_object = context.get_imported_resource(stf_property_path[0])
		component_index = get_component_index(blender_resource, cls.blender_property_name, blender_object.stf_id)
		if(component_index is not None):
			match(stf_property_path[1]):
				case "weight":
					return BlenderPropertyPathPart("OBJECT", cls.blender_property_name + "[" + str(component_index) + "].weight")
				case "enabled":
					return BlenderPropertyPathPart("OBJECT", cls.blender_property_name + "[" + str(component_index) + "].enabled")
		return None


	@classmethod
	def update_component_instance(cls, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: STFEXP_Constraint_Twist, component_instance: STFEXP_Constraint_Twist):
		component_instance.weight = component.weight
		# If the target bone is empty, the parent of the parent is assumed. In that case do not set the default target_object.
		component_instance.source.target_object = context_resource if component.source.target_bone else None
		component_instance.source.target_bone = component.source.target_bone

	@classmethod
	def export_component_instance(cls, context: STF_ExportContext, component_ref: STF_Component_Ref, component_instance: STFEXP_Constraint_Twist, context_resource: Any) -> dict:
		ret = { "weight": component_instance.weight }
		def _handle():
			if(source_ret := node_path_selector_to_stf(context, component_instance.source, ret)):
				ret["source"] = source_ret
		context.add_task(STF_TaskSteps.DEFAULT, _handle)
		return ret

	@classmethod
	def import_component_instance(cls, context: STF_ImportContext, json_resource: dict, component_ref: STF_Component_Ref, component_instance: STFEXP_Constraint_Twist, context_resource: Any):
		if("weight" in json_resource): component_instance.weight = json_resource["weight"]
		if("source" in json_resource and len(json_resource["source"]) > 0):
			_get_component = preserve_component_reference(component_instance, cls.blender_property_name, context_resource)
			def _handle():
				standin_component = _get_component()
				node_path_selector_from_stf(context, json_resource, json_resource["source"], standin_component.source)
			context.add_task(STF_TaskSteps.DEFAULT, _handle)


def register():
	setattr(bpy.types.Object, Handler_STFEXP_Constraint_Twist.blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist, options=set()))
	setattr(bpy.types.Bone, Handler_STFEXP_Constraint_Twist.blender_property_name, bpy.props.CollectionProperty(type=STFEXP_Constraint_Twist, options=set()))

def unregister():
	if hasattr(bpy.types.Object, Handler_STFEXP_Constraint_Twist.blender_property_name):
		delattr(bpy.types.Object, Handler_STFEXP_Constraint_Twist.blender_property_name)
	if hasattr(bpy.types.Bone, Handler_STFEXP_Constraint_Twist.blender_property_name):
		delattr(bpy.types.Bone, Handler_STFEXP_Constraint_Twist.blender_property_name)
