import bpy

from .ft_csv import ft_definitions
from ....base.stf_module_component import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref
from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import add_component, export_component_base, import_component_base
from ....utils.misc import OpenWebpage


_stf_type = "ava.face_tracking.blendshape"
_blender_property_name = "ava_face_tracking_blendshape"


def _match_ft_blendshapes(mesh: bpy.types.Mesh, shapes: list[str]) -> tuple[int, int]:
	if(not mesh.shape_keys or not mesh.shape_keys.key_blocks): return 0
	shapes_matched = 0
	for shape in shapes:
		if(shape in mesh.shape_keys.key_blocks.keys()):
			shapes_matched += 1
	return (shapes_matched, len(shapes))


class AVA_FaceTracking_Blendshapes(STF_BlenderComponentBase):
	ft_type: bpy.props.EnumProperty(items=[("unified_expressions", "Unified Expressions (Preferred)", ""),("arkit", "ARkit", ""),("sranipal", "SRanipal", ""),("facs_reduced", "FACS Reduced (Quest Pro)", ""),("other", "Unknown Tracking Type", "")], name="Type", default="unified_expressions", options=set()) # type: ignore
	ft_type_custom: bpy.props.StringProperty(name="Unknown Tracking Type", options=set()) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: bpy.types.Mesh, component: AVA_FaceTracking_Blendshapes):
	row = layout.row()
	row.operator(OpenWebpage.bl_idname, text="VRCFT Documentation", icon="HELP").url = "https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/overview"
	row.operator(OpenWebpage.bl_idname, text="Mappings Definition", icon="DOCUMENTS").url = "https://docs.google.com/spreadsheets/d/118jo960co3Mgw8eREFVBsaJ7z0GtKNr52IB4Bz99VTA"

	layout.use_property_split = True
	layout.label(text="Not all shapes are required, consult the above links to learn more!", icon="INFO")
	layout.prop(component, "ft_type")

	if(component.ft_type != "other"):
		shape_match = _match_ft_blendshapes(context_object, ft_definitions[component.ft_type])
		split = layout.split(factor=0.4); split.row(); split.label(text=str(shape_match[0]) + " / " + str(shape_match[1]) + " Matched")
	else:
		layout.prop(component, "ft_type_custom")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, context_object: bpy.types.Mesh) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, id, _stf_type)
	import_component_base(context, component, json_resource, _blender_property_name, context_object)
	if("ft_type" in json_resource):
		if(json_resource["ft_type"] in ft_definitions):
			component.ft_type = json_resource["ft_type"]
		else:
			component.ft_type = "other"
			component.ft_type_custom= json_resource["ft_type"]
	return component


def _stf_export(context: STF_ExportContext, component: AVA_FaceTracking_Blendshapes, context_object: bpy.types.Mesh) -> tuple[dict, str]:
	ret = export_component_base(context, _stf_type, component, _blender_property_name, context_object)
	if(component.ft_type != "other"):
		ret["ft_type"] = component.ft_type
	else:
		ret["ft_type"] = component.ft_type_custom
	return ret, component.stf_id


class STF_Module_AVA_FaceTracking_Blendshapes(STF_BlenderComponentModule):
	"""Define face-tracking blendshapes"""
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_FaceTracking_Blendshapes]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_FaceTracking_Blendshapes
]


def register():
	setattr(bpy.types.Mesh, _blender_property_name, bpy.props.CollectionProperty(type=AVA_FaceTracking_Blendshapes, options=set()))

def unregister():
	if hasattr(bpy.types.Mesh, _blender_property_name):
		delattr(bpy.types.Mesh, _blender_property_name)

