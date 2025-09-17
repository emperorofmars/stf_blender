import bpy

from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base


_stf_type = "ava.visemes.blendshape"
_blender_property_name = "stf_ava_visemes_blendshape"


_voice_visemes_15 = ["sil", "aa", "ch", "dd", "e", "ff", "ih", "kk", "nn", "oh", "ou", "pp", "rr", "ss", "th"]
_voice_visemes_15_prefixes = ["", "vis.", "vis_", "vis ", "vrc.", "vrc_", "vrc "]

class AVA_Visemes_Blendshape(STF_BlenderComponentBase):
	vis_sil: bpy.props.StringProperty(name="Sil") # type: ignore
	vis_pp: bpy.props.StringProperty(name="PP") # type: ignore
	vis_ff: bpy.props.StringProperty(name="FF") # type: ignore
	vis_th: bpy.props.StringProperty(name="TH") # type: ignore
	vis_dd: bpy.props.StringProperty(name="DD") # type: ignore
	vis_kk: bpy.props.StringProperty(name="KK") # type: ignore
	vis_ch: bpy.props.StringProperty(name="CH") # type: ignore
	vis_ss: bpy.props.StringProperty(name="SS") # type: ignore
	vis_nn: bpy.props.StringProperty(name="NN") # type: ignore
	vis_rr: bpy.props.StringProperty(name="RR") # type: ignore
	vis_aa: bpy.props.StringProperty(name="AA") # type: ignore
	vis_e: bpy.props.StringProperty(name="E") # type: ignore
	vis_ih: bpy.props.StringProperty(name="IH") # type: ignore
	vis_oh: bpy.props.StringProperty(name="OH") # type: ignore
	vis_ou: bpy.props.StringProperty(name="OU") # type: ignore


class AutomapVisemes(bpy.types.Operator):
	"""Map from Names"""
	bl_idname = "ava.ava_map_blendshape_visemes"
	bl_label = "Map from Names"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		for component in context.mesh.stf_ava_visemes_blendshape:
			if(component.stf_id == self.component_id):
				break

		for viseme in _voice_visemes_15:
			component["vis_" + viseme] = ""

		if(context.mesh.shape_keys):
			for shape_key in context.mesh.shape_keys.key_blocks:
				for viseme in _voice_visemes_15:
					for prefix in _voice_visemes_15_prefixes:
						if(shape_key.name.lower().find(prefix + viseme) > 0 and (len(getattr(component, "vis_" + viseme)) > len(shape_key.name) or len(getattr(component, "vis_" + viseme)) == 0)):
							component["vis_" + viseme] = shape_key.name

		return {"FINISHED"}


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_Visemes_Blendshape):
	layout.operator(AutomapVisemes.bl_idname).component_id = component.stf_id

	layout.prop(component, "vis_sil")
	layout.prop(component, "vis_pp")
	layout.prop(component, "vis_ff")
	layout.prop(component, "vis_th")
	layout.prop(component, "vis_dd")
	layout.prop(component, "vis_kk")
	layout.prop(component, "vis_ch")
	layout.prop(component, "vis_ss")
	layout.prop(component, "vis_nn")
	layout.prop(component, "vis_rr")
	layout.prop(component, "vis_aa")
	layout.prop(component, "vis_e")
	layout.prop(component, "vis_ih")
	layout.prop(component, "vis_oh")
	layout.prop(component, "vis_ou")



def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	for viseme in _voice_visemes_15:
		if(viseme in json_resource):
			component["vis_" + viseme] = json_resource[viseme]

	return component


def _stf_export(context: STF_ExportContext, component: AVA_Visemes_Blendshape, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)

	for viseme in _voice_visemes_15:
		ret[viseme] = component["vis_" + viseme]

	return ret, component.stf_id


class STF_Module_AVA_Visemes_Blendshape(STF_BlenderComponentModule):
	"""Define which shape-keys/blendshapes represent visemes"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_Visemes_Blendshape]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_Visemes_Blendshape
]


def register():
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=AVA_Visemes_Blendshape))

def unregister():
	if hasattr(bpy.types.Mesh, _blender_property_name):
		delattr(bpy.types.Mesh, _blender_property_name)
