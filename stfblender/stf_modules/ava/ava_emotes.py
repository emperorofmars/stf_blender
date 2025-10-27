import bpy

from ...base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ...exporter.stf_export_context import STF_ExportContext
from ...importer.stf_import_context import STF_ImportContext
from ...utils.component_utils import add_component, export_component_base, import_component_base
from ...base.stf_report import STFReport, STFReportSeverity
from ...utils.reference_helper import register_exported_resource, import_resource
from ...utils.misc import draw_slot_link_warning
from ...base.blender_grr import *
from ...utils.helpers import create_add_button, create_remove_button


_stf_type = "ava.emotes"
_blender_property_name = "ava_emotes"


emote_values = (
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

class AVA_Emote(bpy.types.PropertyGroup):
	emote: bpy.props.EnumProperty(name="Emote", items=emote_values, description="The semantic meaning of the mapped animation", options=set()) # type: ignore
	custom_emote: bpy.props.StringProperty(name="Custom Emote", options=set()) # type: ignore

	animation: bpy.props.PointerProperty(type=bpy.types.Action, name="Animation", description="The animation which represents the emote", options=set()) # type: ignore # todo select only actions with a valid slot-link setup

	use_blendshape_fallback: bpy.props.BoolProperty(name="Provide Blendshape Only Fallback", default=False, description="Some targets like VRM have a very limited system for avatar expressions. Provide a blendshape-only pose for these applications", options=set()) # type: ignore
	blendshape_fallback: bpy.props.PointerProperty(type=STFDataResourceReference, options=set()) # type: ignore


class AVA_Emotes(STF_BlenderComponentBase):
	emotes: bpy.props.CollectionProperty(type=AVA_Emote) # type: ignore
	active_emote: bpy.props.IntProperty() # type: ignore


class STFDrawAVAEmoteList(bpy.types.UIList):
	bl_idname = "COLLECTION_UL_ava_emote_list"

	sort_reverse: bpy.props.BoolProperty(default=False, name="Reverse") # type: ignore
	sort_by: bpy.props.EnumProperty(items=[("original", "Added Order", "", "SORTSIZE", 0),("emote", "Emote", "", "NONE", 1)], name="Sort by")# type: ignore
	filter_emote: bpy.props.StringProperty(name="Filter Emote")# type: ignore

	def draw_filter(self, context: bpy.types.Context, layout: bpy.types.UILayout):
		row = layout.row(align=True)
		row_l = row.row(align=True)
		row_l.alignment = "LEFT"
		row.prop(self, "filter_emote", text="", placeholder="Filter Emote", icon="FILTER")
		row.prop(self, "sort_by", text="", icon="SORTSIZE")
		row_r = row.row(align=True)
		row_r.alignment = "RIGHT"
		row_r.prop(self, "sort_reverse", text="", icon="SORT_DESC" if self.sort_reverse else "SORT_ASC")

	def filter_items(self, context: bpy.types.Context, data, propname: str):
		items: list[AVA_Emote] = getattr(data, propname)

		filter = [self.bitflag_filter_item] * len(items)
		if(self.filter_emote):
			for idx, item in enumerate(items):
				filter_match = True
				if(self.filter_emote):
					if(item.emote != "custom" and not (self.filter_emote.lower() in item.emote.lower() or item.emote.lower() in self.filter_emote.lower())):
						filter_match = False
					elif( not (self.filter_emote.lower() in item.custom_emote.lower() or item.custom_emote.lower() in self.filter_emote.lower())):
						filter_match = False
				if(not filter_match):
					filter[idx] = ~self.bitflag_filter_item

		_sort = [(idx, item) for idx, item in enumerate(items)]
		def _sort_func(item: tuple[int, AVA_Emote]):
			match(self.sort_by):
				case "emote":
					if(item[1].emote != "custom"):
						return item[1].emote
					else:
						return item[1].custom_emote
				case _:
					return item[0]
		sortorder = bpy.types.UI_UL_list.sort_items_helper(_sort, _sort_func, self.sort_reverse)

		return filter, sortorder

	def draw_item(self, context: bpy.types.Context, layout: bpy.types.UILayout, data, item: AVA_Emote, icon, active_data, active_propname, index):
		layout.label(text=item.custom_emote.capitalize() if item.emote == "custom" else str(item.emote).capitalize())
		if(item.animation): layout.label(text=item.animation.name, icon="ACTION")
		if(item.use_blendshape_fallback and validate_stf_data_resource_reference(item.blendshape_fallback)):
			layout.label(text="Has Fallback", icon="CHECKMARK")
		else:
			layout.label(text="No Fallback", icon="X")


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Emotes):
	if(not hasattr(bpy.types.Action, "slot_links")):
		draw_slot_link_warning(layout)

	layout.use_property_split = True

	create_add_button(layout, "collection" if context_object != context.scene.collection else True, _blender_property_name, component.stf_id, "emotes", text="Add Emote")

	row = layout.row(align=True)
	row.template_list(STFDrawAVAEmoteList.bl_idname, "", component, "emotes", component, "active_emote")
	if(component.active_emote >= len(component.emotes)):
		return

	create_remove_button(row, "collection" if context_object != context.scene.collection else True, _blender_property_name, component.stf_id, "emotes", component.active_emote)

	emote = component.emotes[component.active_emote]

	box = layout.box()
	row = box.row()
	row.prop(emote, "emote")

	if(emote.emote == "custom"):
		box.prop(emote, "custom_emote")

	box.prop(emote, "animation")
	box.label(text="Note: the animation must have valid 'Slot Link' targets.", icon="INFO_LARGE")

	box.separator(factor=1, type="LINE")
	box.use_property_split = False
	box.prop(emote, "use_blendshape_fallback")

	if(emote.use_blendshape_fallback):
		box = box.box()
		box.label(text="Blendshape Only Fallback (For VRM)")
		if(not validate_stf_data_resource_reference(emote.blendshape_fallback, ["dev.vrm.blendshape_pose"])):
			box.label(text="Create a 'dev.vrm.blendshape_pose' type resource in a Blender-Collection under 'STF Data Resources'.", icon="INFO_LARGE")
		box.use_property_split = True
		draw_stf_data_resource_reference(box.column(align=True), emote.blendshape_fallback, ["dev.vrm.blendshape_pose"])


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(context, component, json_resource)

	def _handle():
		for meaning, json_emote in json_resource.get("emotes", {}).items():
			blender_emote: AVA_Emote = component.emotes.add()
			for enum_value in emote_values:
				if(enum_value[0] == meaning):
					blender_emote.emote = enum_value[0]
					break
			else:
				blender_emote.emote = "custom"
				blender_emote.custom_emote = meaning
			blender_emote.animation = import_resource(context, json_resource, json_emote.get("animation"), "data")

			if("fallback" in json_emote):
				blender_emote.use_blendshape_fallback = True
				if(fallback_resource := import_resource(context, json_resource, json_emote["fallback"], "data")):
					blender_emote.blendshape_fallback.collection = context.get_root_collection() # todo maybe handle root collection import?
					blender_emote.blendshape_fallback.stf_data_resource_id = fallback_resource.stf_id
				else:
					context.report(STFReport("module: %s stf_id: %s, context-object: %s" % (_stf_type, stf_id, context_object), STFReportSeverity.Warn, stf_id, _stf_type, context_object))

	context.add_task(_handle)

	return component


def _stf_export(context: STF_ExportContext, component: AVA_Emotes, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)

	emotes = {}
	ret["emotes"] = emotes

	def _handle():
		for blender_emote in component.emotes:
			blender_emote: AVA_Emote = blender_emote
			meaning = blender_emote.emote if blender_emote.emote != "custom" else blender_emote.custom_emote
			animation_id = context.get_resource_id(blender_emote.animation)

			if(meaning and animation_id):
				json_emote = { "animation": register_exported_resource(ret, animation_id) }
				emotes[meaning] = json_emote

				if(blender_emote.use_blendshape_fallback):
					if(fallback_ret := resolve_stf_data_resource_reference(blender_emote.blendshape_fallback)):
						fallback_ref, fallback_resource = fallback_ret
						if(fallback_ref.stf_type == "dev.vrm.blendshape_pose"):
							json_emote["fallback"] = register_exported_resource(ret, context.serialize_resource(fallback_resource))
						else:
							context.report(STFReport("module: %s stf_id: %s, context-object: %s :: blendshape fallback invalid resource type" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))
					else:
						context.report(STFReport("module: %s stf_id: %s, context-object: %s :: failed to resolve blendshape fallback" % (_stf_type, component.stf_id, context_object), STFReportSeverity.Warn, component.stf_id, _stf_type, context_object))
			else:
				context.report(STFReport("Invalid Emote", STFReportSeverity.Info, component.stf_id, _stf_type, component))

	context.add_task(_handle)

	return ret, component.stf_id


class STF_Module_AVA_Emotes(STF_BlenderComponentModule):
	"""Map facial-expressions/emotions to animations"""
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["emotes"]
	understood_application_types = [AVA_Emotes]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Collection]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_Emotes
]


def register():
	setattr(bpy.types.Collection, _blender_property_name, bpy.props.CollectionProperty(type=AVA_Emotes, options=set()))

def unregister():
	if hasattr(bpy.types.Collection, _blender_property_name):
		delattr(bpy.types.Collection, _blender_property_name)
