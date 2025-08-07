import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....base.stf_report import STFReport, STFReportSeverity
from ....utils.reference_helper import export_resource
from ....utils.minsc import draw_slot_link_warning


_stf_type = "ava.emotes"
_blender_property_name = "ava_emotes"


class Edit_AVA_Emotes(bpy.types.Operator):
	bl_idname = "stf.edit_ava_emotes"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	op: bpy.props.BoolProperty() # type: ignore
	index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		if(self.op):
			for component in context.collection.ava_emotes:
				if(component.stf_id == self.component_id):
					component.emotes.add()
					return {"FINISHED"}
		else:
			for component in context.collection.ava_emotes:
				if(component.stf_id == self.component_id):
					component.emotes.remove(self.index)
					return {"FINISHED"}
		self.report({"ERROR"}, "Couldn't edit Physbone")
		return {"CANCELLED"}


class Edit_AVA_EmoteFallback(bpy.types.Operator):
	bl_idname = "stf.edit_ava_emote_fallback"
	bl_label = "Edit"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	op: bpy.props.BoolProperty() # type: ignore
	emote_index: bpy.props.IntProperty() # type: ignore
	blendshape_index: bpy.props.IntProperty() # type: ignore

	def execute(self, context):
		if(self.op):
			for component in context.collection.ava_emotes:
				if(component.stf_id == self.component_id):
					component.emotes[self.emote_index].blendshape_fallback.values.add()
					return {"FINISHED"}
		else:
			for component in context.collection.ava_emotes:
				if(component.stf_id == self.component_id):
					component.emotes[self.emote_index].blendshape_fallback.values.remove(self.blendshape_index)
					return {"FINISHED"}
		self.report({"ERROR"}, "Couldn't edit Physbone")
		return {"CANCELLED"}


class AVA_FallbackBlendshape_Value(bpy.types.PropertyGroup):
	mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Meshinstance", poll=lambda s, o: o.data and type(o.data) == bpy.types.Mesh) # type: ignore
	blendshape_name: bpy.props.StringProperty(name="Name") # type: ignore
	blendshape_value: bpy.props.FloatProperty(name="Value", default=0, soft_min=0, soft_max=1, subtype="FACTOR") # type: ignore

class AVA_FallbackBlendshape_Emote(bpy.types.PropertyGroup):
	values: bpy.props.CollectionProperty(type=AVA_FallbackBlendshape_Value) # type: ignore


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
	("surpriced", "Surpriced", ""),
	("scared", "Scared", ""),
	("disgusted", "Disgusted", ""),
	("embarassed", "Embarassed", ""),
	("dumb", "Dumb", ""),
	("silly", "Silly", ""),
	("evil", "Evil", ""),
	("aaa", "AAA", ""),
	("custom", "Custom", "")
	# todo define many more
)

class AVA_Emote(bpy.types.PropertyGroup):
	emote: bpy.props.EnumProperty(name="Emote", items=emote_values) # type: ignore
	custom_emote: bpy.props.StringProperty(name="Custom Emote") # type: ignore

	animation: bpy.props.PointerProperty(type=bpy.types.Action, name="Animation") # type: ignore # todo select only actions with a valid slot-link setup

	use_blendshape_fallback: bpy.props.BoolProperty(name="Provide Blendshape Only Fallback", default=False) # type: ignore
	blendshape_fallback: bpy.props.PointerProperty(type=AVA_FallbackBlendshape_Emote, name="Blendshape Only Fallback") # type: ignore


class AVA_Emotes(STF_BlenderComponentBase):
	emotes: bpy.props.CollectionProperty(type=AVA_Emote) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Emotes):
	row = layout.row()
	row.label(text="Emotes")
	
	if(not hasattr(bpy.types.Action, "slot_links")):
		draw_slot_link_warning(layout)

	add_button = layout.operator(Edit_AVA_Emotes.bl_idname, text="Add")
	add_button.component_id = component.stf_id
	add_button.op = True

	for index, emote in enumerate(component.emotes):
		box = layout.box()

		row = box.row()
		row.prop(emote, "emote")
		remove_button = row.operator(Edit_AVA_Emotes.bl_idname, text="", icon="X")
		remove_button.component_id = component.stf_id
		remove_button.op = False
		remove_button.index = index

		if(emote.emote == "custom"):
			box.prop(emote, "custom_emote")

		layout.label(text="Note: the animation must have a valid 'Slot Link' target.")
		box.prop(emote, "animation")

		box.separator(factor=1, type="LINE")
		box.prop(emote, "use_blendshape_fallback")
		if(emote.use_blendshape_fallback):
			box = box.box()
			box.label(text="Blendshape Only Fallback")

			add_button = box.operator(Edit_AVA_EmoteFallback.bl_idname, text="Add Blendshape")
			add_button.component_id = component.stf_id
			add_button.op = True
			add_button.emote_index = index
			for blendshape_index, blendshape in enumerate(emote.blendshape_fallback.values):
				inner_row = box.row()
				inner_row.prop(blendshape, "mesh_instance", text="")
				if(blendshape.mesh_instance and type(blendshape.mesh_instance.data) == bpy.types.Mesh):
					inner_row.prop_search(blendshape, "blendshape_name", blendshape.mesh_instance.data.shape_keys, "key_blocks", text="")
					inner_row.prop(blendshape, "blendshape_value", text="")
				remove_button = inner_row.operator(Edit_AVA_EmoteFallback.bl_idname, text="", icon="X")
				remove_button.component_id = component.stf_id
				remove_button.op = False
				remove_button.emote_index = index
				remove_button.blendshape_index = blendshape_index


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)

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
			blender_emote.animation = context.get_imported_resource(json_emote.get("animation"))
			
			if("fallback" in json_emote):
				blender_emote.use_blendshape_fallback = True
				for fallback in json_emote["fallback"]:
					if(mesh_instance := context.get_imported_resource(fallback["mesh_instance"])):
						blender_fallback = blender_emote.blendshape_fallback.values.add()
						blender_fallback.mesh_instance = mesh_instance
						blender_fallback.blendshape_name = fallback["name"]
						blender_fallback.blendshape_value = fallback["value"]

	context.add_task(_handle)

	return component


def _stf_export(context: STF_ExportContext, component: AVA_Emotes, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, component)

	emotes = {}
	ret["emotes"] = emotes

	def _handle():
		for blender_emote in component.emotes:
			blender_emote: AVA_Emote = blender_emote
			meaning = blender_emote.emote if blender_emote.emote != "custom" else blender_emote.custom_emote
			animation_id = context.get_resource_id(blender_emote.animation)

			if(meaning and animation_id):
				json_emote = { "animation": export_resource(ret, animation_id) }
				emotes[meaning] = json_emote

				if(blender_emote.use_blendshape_fallback and len(blender_emote.blendshape_fallback.values) > 0):
					fallback = []
					for fallback_blendshape in blender_emote.blendshape_fallback.values:
						if(fallback_blendshape.mesh_instance and fallback_blendshape.blendshape_name):
							fallback.append({
								"mesh_instance": export_resource(ret, context.get_resource_id(fallback_blendshape.mesh_instance)),
								"name": fallback_blendshape.blendshape_name,
								"value": fallback_blendshape.blendshape_value,
							})

					json_emote["fallback"] = fallback
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
	bpy.types.Collection.ava_emotes = bpy.props.CollectionProperty(type=AVA_Emotes) # type: ignore

def unregister():
	if hasattr(bpy.types.Collection, "ava_emotes"):
		del bpy.types.Collection.ava_emotes

