import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....utils.op_utils import OpenWebpage


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


class AVA_FallbackBlendshape_Value(bpy.types.PropertyGroup):
	mesh_instance: bpy.props.PointerProperty(type=bpy.types.Object, name="Meshinstance", poll=lambda s, o: o.data and type(o.data) == bpy.types.Mesh) # type: ignore
	blendshape_name: bpy.props.StringProperty(name="Name") # type: ignore
	blendshape_value: bpy.props.FloatProperty(name="Value", default=0.5) # type: ignore

class AVA_FallbackBlendshape_Emote(bpy.types.PropertyGroup):
	values: bpy.props.CollectionProperty(type=AVA_FallbackBlendshape_Value) # type: ignore


class AVA_Emote(bpy.types.PropertyGroup):
	emote: bpy.props.EnumProperty(name="Emote", items=(("smile", "Smile", ""), ("smirk", "Smirk", ""), ("blep", "Blep", ""), ("sad", "Sad", ""), ("custom", "Custom", ""))) # type: ignore
	custom_emote: bpy.props.StringProperty(name="Custom Emote") # type: ignore

	animation: bpy.props.PointerProperty(type=bpy.types.Action, name="Animation") # type: ignore # todo select only actions with a valid slot-link setup

	eyeblink_tracking: bpy.props.BoolProperty(name="Eyeblink Enabled", default=True) # type: ignore
	breathing_speed: bpy.props.FloatProperty(name="Speed", default=0.5) # type: ignore
	breathing_intensity: bpy.props.FloatProperty(name="Intensity", default=0.5) # type: ignore

	blendshape_fallback: bpy.props.PointerProperty(type=AVA_FallbackBlendshape_Emote, name="Blendshape Only Fallback") # type: ignore


class AVA_Emotes(STF_BlenderComponentBase):
	emotes: bpy.props.CollectionProperty(type=AVA_Emote) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Emotes):
	row = layout.row()
	row.label(text="Emotes")
	
	if(not hasattr(bpy.types.Action, "slot_links")):
		layout.label(text="Note: the 'Slot Link' extension is")
		layout.label(text="required to import & export animations!")
		layout.operator(OpenWebpage.bl_idname).url = "https://extensions.blender.org/add-ons/slot-link/"
		layout.separator(factor=1, type="SPACE")

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
			box.prop(emote, "eyeblink_tracking")
			row_inner = box.row(heading="Breathing", align=True)
			row_inner.prop(emote, "breathing_speed")
			row_inner.prop(emote, "breathing_intensity")

		box.prop(emote, "animation")
		box = box.box()
		box.label(text="Blendshape Only Fallback")
		# todo add op
		for index, blendshape in enumerate(emote.blendshape_fallback.values):
			box.prop(blendshape, "mesh_instance")
			#if(emote.blendshape_fallback.mesh_instance):
			#	box.label(text="TODO blendshape values")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Emotes, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)
	return ret, application_object.stf_id


class STF_Module_AVA_Emotes(STF_BlenderComponentModule):
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

