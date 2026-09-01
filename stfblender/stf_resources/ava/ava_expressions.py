import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STFReportSeverity, STFReport, STF_TaskSteps, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....stfblender_common.helpers import register_exported_resource, create_add_button, create_remove_button, poll_valid_animations, draw_slot_link_warning
from ....stfblender_common.blender_grr import *


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
	expression: bpy.props.EnumProperty(name="Expression", items=expression_values, description="The semantic meaning of the mapped animation", options=set())
	custom_expression: bpy.props.StringProperty(name="Custom Expression", options=set())

	animation: bpy.props.PointerProperty(type=bpy.types.Action, name="Animation", description="The animation which represents the expression", options=set(), poll=poll_valid_animations)

	use_blendshape_fallback: bpy.props.BoolProperty(name="Provide Blendshape Only Fallback", default=False, description="Some targets like VRM have a very limited system for avatar expressions. Provide a blendshape-only pose for these applications", options=set())
	blendshape_fallback: bpy.props.PointerProperty(type=STFNonNativeResourceReference, options=set())


class AVA_Expressions(STF_ComponentResourceBase):
	expressions: bpy.props.CollectionProperty(type=AVA_Expression)
	active_expression: bpy.props.IntProperty()


class STFDrawAVAExpressionList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_ava_expression_list"

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse")
	sort_by: bpy.props.EnumProperty(items=[("original", "Added Order", "", "SORTSIZE", 0),("expression", "Expression", "", "NONE", 1)], name="Sort by")
	filter_expression: bpy.props.StringProperty(name="Filter Expression")

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_expression", text="", placeholder="Filter Expression", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str) -> tuple[list[int], None]: # pyright: ignore[reportIncompatibleMethodOverride]
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

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: AVA_Expression, icon, active_data, active_propname, index): # pyright: ignore[reportIncompatibleMethodOverride]
		layout.label(text=item.custom_expression.capitalize() if item.expression == "custom" else str(item.expression).capitalize())
		if(item.animation):
			layout.label(text=item.animation.name, icon="ACTION")
		else:
			row = layout.row()
			row.alert = True
			row.label(text="No Action", icon="ACTION")
		if(item.use_blendshape_fallback and item.blendshape_fallback.validate()):
			layout.label(text="Has Fallback", icon="CHECKMARK")
		else:
			layout.label(text="No Fallback", icon="X")


class Handler_AVA_Expressions(STF_Handler_Component):
	"""Map facial-expressions/emotions to animations"""
	stf_type = "ava.expressions"
	stf_category = STF_Category.COMPONENT
	like_types = ["expressions"]
	understood_blender_types = [AVA_Expressions]
	blender_property_name = "ava_expressions"
	single = True
	filter = [bpy.types.Collection]
	pretty_name_template = "Avatar Expressions"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: AVA_Expressions):
		if(not hasattr(bpy.types.Action, "slot_links")):
			draw_slot_link_warning(layout)

		layout.use_property_split = True

		create_add_button(layout, "collection" if context_resource != context.scene.collection else True, cls.blender_property_name, component.stf_id, "expressions", text="Add Expression")

		row = layout.row(align=True)
		row.template_list(STFDrawAVAExpressionList.bl_idname, "", component, "expressions", component, "active_expression")
		if(component.active_expression >= len(component.expressions)):
			return

		create_remove_button(row, "collection" if context_resource != context.scene.collection else True, cls.blender_property_name, component.stf_id, "expressions", component.active_expression)

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
			if(not expression.blendshape_fallback.validate(["dev.vrm.blendshape_pose"])):
				box.label(text="Create a 'dev.vrm.blendshape_pose' type resource in a Blender-Collection under 'STF Data Resources'.", icon="INFO_LARGE")
			box.use_property_split = True
			expression.blendshape_fallback.draw(box.column(align=True), ["dev.vrm.blendshape_pose"])

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

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

				if("animation" in json_expression):
					expression_anim = context.import_resource(json_resource, json_expression.get("animation"), STF_Category.DATA)
					if(type(expression_anim) is bpy.types.Action):
						blender_expression.animation = expression_anim

				if("fallback" in json_expression):
					blender_expression.use_blendshape_fallback = True
					if(fallback_resource := context.import_resource(json_resource, json_expression["fallback"], STF_Category.DATA)):
						blender_expression.blendshape_fallback.collection = context.get_root_collection() # TODO maybe handle root collection import?
						blender_expression.blendshape_fallback.stf_data_resource_id = fallback_resource.stf_id
					else:
						context.report(STFReport("module: %s stf_id: %s, context-object: %s" % (cls.stf_type, stf_id, context_resource), STFReportSeverity.Warn, stf_id, cls.stf_type, context_resource))

		context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: AVA_Expressions, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)

		expressions = {}
		ret["expressions"] = expressions

		def _handle():
			for blender_expression in component.expressions:
				blender_expression: AVA_Expression = blender_expression
				meaning = blender_expression.expression if blender_expression.expression != "custom" else blender_expression.custom_expression
				if(not meaning):
					context.report(STFReport("Invalid Expression, no meaning defined", STFReportSeverity.Info, component.stf_id, cls.stf_type, component))

				json_expression = {}
				any_success = False

				animation_id = context.get_resource_id(blender_expression.animation)
				if(animation_id):
					json_expression["animation"] = register_exported_resource(ret, animation_id)
					any_success = True

				if(blender_expression.use_blendshape_fallback):
					if(fallback_ret := blender_expression.blendshape_fallback.resolve()):
						fallback_ref, fallback_resource = fallback_ret
						if(fallback_ref.stf_type == "dev.vrm.blendshape_pose"):
							json_expression["fallback"] = context.serialize_resource(ret, fallback_resource, stf_category=STF_Category.DATA)
							any_success = True
						else:
							context.report(STFReport("module: %s stf_id: %s, context-object: %s :: blendshape fallback invalid resource type" % (cls.stf_type, component.stf_id, context_resource), STFReportSeverity.Warn, component.stf_id, cls.stf_type, context_resource))
					else:
						context.report(STFReport("module: %s stf_id: %s, context-object: %s :: failed to resolve blendshape fallback" % (cls.stf_type, component.stf_id, context_resource), STFReportSeverity.Warn, component.stf_id, cls.stf_type, context_resource))

				if(any_success):
					expressions[meaning] = json_expression

		context.add_task(STF_TaskSteps.AFTER_ANIMATION, _handle)

		return ret, component.stf_id


def register():
	setattr(bpy.types.Collection, Handler_AVA_Expressions.blender_property_name, bpy.props.CollectionProperty(type=AVA_Expressions, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, Handler_AVA_Expressions.blender_property_name):
		delattr(bpy.types.Collection, Handler_AVA_Expressions.blender_property_name)
