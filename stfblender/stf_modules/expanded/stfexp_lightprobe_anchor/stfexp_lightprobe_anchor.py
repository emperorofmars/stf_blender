import bpy

from ....base.stf_module import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base
from ....utils.reference_helper import export_resource


_stf_type = "stfexp.lightprobe_anchor"
_blender_property_name = "stfexp_lightprobe_anchor"


class STFEXP_LightprobeAnchor(STF_BlenderComponentBase):
	anchor_object: bpy.props.PointerProperty(type=bpy.types.Object, name="Anchor Object") # type: ignore
	anghor_bone: bpy.props.StringProperty(name="Anchor Bone") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: STFEXP_LightprobeAnchor):
	layout.prop(component, "anchor_object")
	if(component.anchor_object and type(component.anchor_object.data) == bpy.types.Armature):
		layout.prop_search(component, "anghor_bone", component.anchor_object.data, "bones")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	if("anchor" in json_resource):
		if(len(json_resource["anchor"]) == 1):
			def _handle_target_object():
				component.anchor_object = context.get_imported_resource(json_resource["anchor"][0])
			context.add_task(_handle_target_object)
		elif(len(json_resource["anchor"]) == 3):
			def _handle_target_object():
				component.anchor_object = context.get_imported_resource(json_resource["anchor"][0])
			context.add_task(_handle_target_object)
			def _handle_target_bone():
				component.anghor_bone = context.get_imported_resource(json_resource["anchor"][2]).name
			context.add_task(_handle_target_bone)

	return component


def _stf_export(context: STF_ExportContext, component: STFEXP_LightprobeAnchor, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component)

	if(component.anchor_object):
		def _handle():
			if(type(component.anchor_object.data) == bpy.types.Armature and component.anghor_bone):
				ret["anchor"] = [export_resource(ret, component.anchor_object.stf_id), "instance", export_resource(ret, component.anchor_object.data.bones[component.anghor_bone].stf_id)]
			else:
				ret["anchor"] = [export_resource(ret, component.anchor_object.stf_id)]

		context.add_task(_handle)

	return ret, component.stf_id


class STF_Module_STFEXP_LightprobeAnchor(STF_BlenderComponentModule):
	"""Define a object/bone from which a game-engine will sample lightprobe values"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [STFEXP_LightprobeAnchor]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Object]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_STFEXP_LightprobeAnchor
]


def register():
	bpy.types.Object.stfexp_lightprobe_anchor = bpy.props.CollectionProperty(type=STFEXP_LightprobeAnchor) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "stfexp_lightprobe_anchor"):
		del bpy.types.Object.stfexp_lightprobe_anchor

