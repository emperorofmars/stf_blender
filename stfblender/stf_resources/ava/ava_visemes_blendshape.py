import bpy
from typing import Any

from ....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STFReport, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, add_component, export_component_base, import_component_base


_voice_visemes_15 = ["sil", "aa", "ch", "dd", "e", "ff", "ih", "kk", "nn", "oh", "ou", "pp", "rr", "ss", "th"]
_voice_visemes_15_prefixes = ["vis.", "vis_", "vis ", "vrc.", "vrc_", "vrc ", "vrc.v_", "viseme", "viseme.", "viseme_", "viseme ", ""]

class AVA_Visemes_Blendshape(STF_ComponentResourceBase):
	vis_sil: bpy.props.StringProperty(name="Sil", options=set())
	vis_pp: bpy.props.StringProperty(name="PP", options=set())
	vis_ff: bpy.props.StringProperty(name="FF", options=set())
	vis_th: bpy.props.StringProperty(name="TH", options=set())
	vis_dd: bpy.props.StringProperty(name="DD", options=set())
	vis_kk: bpy.props.StringProperty(name="KK", options=set())
	vis_ch: bpy.props.StringProperty(name="CH", options=set())
	vis_ss: bpy.props.StringProperty(name="SS", options=set())
	vis_nn: bpy.props.StringProperty(name="NN", options=set())
	vis_rr: bpy.props.StringProperty(name="RR", options=set())
	vis_aa: bpy.props.StringProperty(name="AA", options=set())
	vis_e: bpy.props.StringProperty(name="E", options=set())
	vis_ih: bpy.props.StringProperty(name="IH", options=set())
	vis_oh: bpy.props.StringProperty(name="OH", options=set())
	vis_ou: bpy.props.StringProperty(name="OU", options=set())


def automap(component: AVA_Visemes_Blendshape, mesh: bpy.types.Mesh):
	for viseme in _voice_visemes_15:
		component["vis_" + viseme] = ""

	confidences: dict[str, int] = {}
	for viseme in _voice_visemes_15:
		confidences[viseme] = -1

	if(mesh.shape_keys):
		for shape_key in mesh.shape_keys.key_blocks:
			for viseme in _voice_visemes_15:
				for prefix in _voice_visemes_15_prefixes:
					test = prefix + viseme
					shape: str = shape_key.name.lower()
					shape_confidence = len(test) / max(len(shape), 1)

					if(test in shape and shape_confidence > confidences[viseme]):
						component["vis_" + viseme] = shape_key.name
						confidences[viseme] = shape_confidence # pyright: ignore[reportArgumentType]


class AutomapVisemes(bpy.types.Operator):
	"""Map from Names"""
	bl_idname = "ava.ava_map_blendshape_visemes"
	bl_label = "Map from Names"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty()

	def execute(self, context) -> set:
		for component in context.mesh.stf_ava_visemes_blendshape:
			if(component.stf_id == self.component_id):
				automap(component, context.mesh) # pyright: ignore[reportArgumentType]
				return {"FINISHED"}
		else:
			return {"CANCELLED"}


class Handler_AVA_Visemes_Blendshape(STF_Handler_Component):
	"""Define which shape-keys/blendshapes represent visemes"""
	stf_type = "ava.visemes.blendshape"
	stf_category = STF_Category.COMPONENT
	like_types = []
	understood_blender_types = [AVA_Visemes_Blendshape]
	blender_property_name = "stf_ava_visemes_blendshape"
	single = True
	filter = [bpy.types.Mesh]
	pretty_name_template = "Viseme Blendshapes"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: Any, component: AVA_Visemes_Blendshape):
		if(not context_resource or type(context_resource) is not bpy.types.Mesh):
			return

		layout.use_property_split = True
		layout.operator(AutomapVisemes.bl_idname, icon="LOOP_FORWARDS").component_id = component.stf_id

		col = layout.column(align=True)
		col.prop_search(component, "vis_sil", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_pp", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_ff", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_th", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_dd", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_kk", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_ch", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_ss", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_nn", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_rr", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_aa", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_e", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_ih", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_oh", context_resource.shape_keys, "key_blocks")
		col.prop_search(component, "vis_ou", context_resource.shape_keys, "key_blocks")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: Any) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)

		for viseme in _voice_visemes_15:
			if(viseme in json_resource):
				component["vis_" + viseme] = json_resource[viseme]

		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: AVA_Visemes_Blendshape, context_resource: Any) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)

		for viseme in _voice_visemes_15:
			ret[viseme] = component["vis_" + viseme]

		return ret, component.stf_id


def register():
	setattr(bpy.types.Mesh, Handler_AVA_Visemes_Blendshape.blender_property_name, bpy.props.CollectionProperty(type=AVA_Visemes_Blendshape, options=set()))

def unregister():
	if hasattr(bpy.types.Mesh, Handler_AVA_Visemes_Blendshape.blender_property_name):
		delattr(bpy.types.Mesh, Handler_AVA_Visemes_Blendshape.blender_property_name)
