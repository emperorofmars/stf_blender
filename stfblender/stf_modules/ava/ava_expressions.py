import bpy

from ...base.stf_task_steps import STF_TaskSteps
from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base
from ...base.stf_report import STFReport, STFReportSeverity
from ...utils.reference_helper import register_exported_resource, import_resource
from ...utils.misc import draw_slot_link_warning
from ...base.blender_grr import *
from ...utils.helpers import create_add_button, create_remove_button


_stf_type = "ava.expressions"
_blender_property_name = "ava_expressions"


expression_values = (
	("smile", "Smile", ""),
	("happy", "Happy", ""),
	("smirk", "Smirk", ""),
	("blep", "Blep", ""),
	("sad", "Sad", ""),
	("afraid", "Afraid", ""),
	("angry", "Angry", ""),
	("grumpy", "Grumpy", ""),
	("suspicious", "Suspicious", ""),
	("disappointed", "Disappointed", ""),
	("surprised", "Surprised", ""),
	("scared", "Scared", ""),
	("disgusted", "Disgusted", ""),
	("embarrassed", "Embarrassed", ""),
	("dumb", "Dumb", ""),
	("silly", "Silly", ""),
	("evil", "Evil", ""),
	("aaa", "AAA", ""),
	("custom", "Custom", "")
	# todo define many more
)

class AVA_Expression(bpy.types.PropertyGroup):
	expression: bpy.props.EnumProperty(name="Expression", items=expression_values, description="The semantic meaning of the mapped animation", options=set()) # type: ignore
	custom_expression: bpy.props.StringProperty(name="Custom Expression", options=set()) # type: ignore

	animation: bpy.props.PointerProperty(type=bpy.types.Action, name="Animation", description="The animation which represents the expression", options=set()) # type: ignore # todo select only actions with a valid slot-link setup

	use_blendshape_fallback: bpy.props.BoolProperty(name="Provide Blendshape Only Fallback", default=False, description="Some targets like VRM have a very limited system for avatar expressions. Provide a blendshape-only pose for these applications", options=set()) # type: ignore
	blendshape_fallback: bpy.props.PointerProperty(type=STFDataResourceReference, options=set()) # type: ignore


class AVA_Expressions(STF_BlenderComponentBase):
	expressions: bpy.props.CollectionProperty(type=AVA_Expression) # type: ignore
	active_expression: bpy.props.IntProperty() # type: ignore


class STFDrawAVAExpressionList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_ava_expression_list"

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse") # type: ignore
	sort_by: bpy.props.EnumProperty(items=[("original", "Added Order", "", "SORTSIZE", 0),("expression", "Expression", "", "NONE", 1)], name="Sort by")# type: ignore
	filter_expression: bpy.props.StringProperty(name="Filter Expression")# type: ignore

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_expression", text="", placeholder="Filter Expression", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[AVA_Expression] = getattr(data, propname)

		filter = [self.bitflag_filter_item] * len(items)
		if(self.filter_expression):
			for idx, item in enumerate(items):
				filter_match = True
				if(self.filter_expression):
					if(item.expression != "custom" and not (self.filter_expression.lower() in item.expression.lower() or item.expression.lower() in self.filter_expression.lower())):
						filter_match = False
					elif( not (self.filter_expression.lower() in item.custom_expression.lower() or item.custom_expression.lower() in self.filter_expression.lower())):
						filter_match = False
				if(not filter_match):
					filter[idx] = ~self.bitflag_filter_item

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, AVA_Expression]):
			match(self.sort_by):
				case "expression":
					if(item[1].expression != "custom"):
						return item[1].expression
					else:
						return item[1].custom_expression
				case _:
					return item[0]
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, self.sort_reverse)

		return filter, sortorder

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: AVA_Expression, icon, active_data, active_propname, index):
		layout.label(text=item.custom_expression.capitalize() if item.expression == "custom" else str(item.expression).capitalize())
		if(item.animation):
			layout.label(text=item.animation.name, icon="ACTION")
		else:
			row = layout.row()
			row.alert = True
			row.label(text="No Action", icon="ACTION")
		if(item.use_blendshape_fallback and validate_stf_data_resource_reference(item.blendshape_fallback)):
			layout.label(text="Has Fallback", icon="CHECKMARK")
		else:
			layout.label(text="No Fallback", icon="X")


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Expressions):
	if(not hasattr(bpy.types.Action, "slot_links")):
		draw_slot_link_warning(layout)

	layout.use_property_split = True

	create_add_button(layout, "collection" if context_object != context.scene.collection else True, _blender_property_name, component.stf_id, "expressions", text="Add Expression")

	row = layout.row(align=True)
	row.template_list(STFDrawAVAExpressionList.bl_idname, "", component, "expressions", component, "active_expression")
	if(component.active_expression >= len(component.expressions)):
		return

	create_remove_button(row, "collection" if context_object != context.scene.collection else True, _blender_property_name, component.stf_id, "expressions", component.active_expression)

	expression = component.expressions[component.active_expression]

	box = layout.box()
	row = box.row()
	row.prop(expression, "expression")

	if(expression.expression == "custom"):
		box.prop(expression, "custom_expression")

	box.prop(expression, "animation")
	box.label(text="Note: the animation must have valid 'Slot Link' targets.", icon="INFO_LARGE")

	box.separator(factor=1, type="LINE")
	box.use_property_split = False
	box.prop(expression, "use_blendshape_fallback")

	if(expression.use_blendshape_fallback):
		box = box.box()
		box.label(text="Blendshape Only Fallback (For VRM)")
		if(not validate_stf_data_resource_reference(expression.blendshape_fallback, ["dev.vrm.blendshape_pose"])):
			box.label(text="Create a 'dev.vrm.blendshape_pose' type resource in a Blender-Collection under 'STF Data Resources'.", icon="INFO_LARGE")
		box.use_property_split = True
		draw_stf_data_resource_reference(box.column(align=True), expression.blendshape_fallback, ["dev.vrm.blendshape_pose"])


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource)

	def _handle():
		for meaning, json_expression in json_resource.get("expressions", {}).items():
			blender_expression: AVA_Expression = component.expressions.add()
			for enum_value in expression_values:
				if(enum_value[0] == meaning):
					blender_expression.expression = enum_value[0]
					break
			else:
				blender_expression.expression = "custom"
				blender_expression.custom_expression = meaning
			blender_expression.animation = import_resource(context, json_resource, json_expression.get("animation"), "data")

			if("fallback" in json_expression):
				blender_expression.use_blendshape_fallback = True
				if(fallback_resource := import_resource(context, json_resource, json_expression["fallback"], "data")):
					blender_expression.blendshape_fallback.collection = context.get_root_collection() # todo maybe handle root collection import?
					blender_expression.blendshape_fallback.stf_data_resource_id = fallback_resource.stf_id
				else:
					context.report(STFReport("module: %s stf_id: %s, context-object: %s" % (_stf_type, stf_id, context_object), STFReportSeverity.Warn, stf_id, _stf_type, context_object))

	context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

	return component


def _stf_export(context: STF_ExportContext, component: AVA_Expressions, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)

	expressions = {}
	ret["expressions"] = expressions

	def _handle():
		for blender_expression in component.expressions:
			blender_expression: AVA_Expression = blender_expression
			meaning = blender_expression.expression if blender_expression.expression != "custom" else blender_expression.custom_expression
			animation_id = context.get_resource_id(blender_expression.animation)

			if(meaning and animation_id):
				json_expression = { "animation": register_exported_resource(ret, animation_id) }
				expressions[meaning] = json_expression

				if(blender_expression.use_blendshape_fallback):
					if(fallback_ret := resolve_stf_data_resource_reference(blender_expression.blendshape_fallback)):
						fallback_ref, fallback_resource = fallback_ret
						if(fallback_ref.stf_type == "dev.vrm.blendshape_pose"):
							json_expression["fallback"] = register_exported_resource(ret, context.serialize_resource(fallback_resource))
						else:
							context.report(STFReport("module: %s stf_id: %s, context-object: %s :: blendshape fallback invalid resource type" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))
					else:
						context.report(STFReport("module: %s stf_id: %s, context-object: %s :: failed to resolve blendshape fallback" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))
			else:
				context.report(STFReport("Invalid Expression", STFReportSeverity.Info, component.stf_id, _stf_type, component))

	context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

	return ret, component.stf_id


class STF_Module_AVA_Expressions(STF_BlenderComponentModule):
	"""Map facial-expressions/emotions to animations"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["expressions"]
	understood_application_types = [AVA_Expressions]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_Expressions
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=AVA_Expressions, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
