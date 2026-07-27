import bpy
from typing import Any

from .ft_csv import ft_definitions
from .....stfblender_common import STF_ExportContext, STF_ImportContext, STF_Category, STF_ComponentResourceBase, STF_Handler_Component, STF_Component_Ref, STFReport, add_component, export_component_base, import_component_base


def _match_ft_blendshapes(mesh: bpy.types.Mesh, shapes: list[str]) -> tuple[int, int]:
	if(not mesh.shape_keys or not mesh.shape_keys.key_blocks): return (0, 0)
	shapes_matched = 0
	for shape in shapes:
		if(shape in mesh.shape_keys.key_blocks.keys()):
			shapes_matched += 1
	return (shapes_matched, len(shapes))


def automap(mesh: bpy.types.Mesh) -> str | None:
	best = None
	best_percent = 0
	for ft_type in ft_definitions:
		matched, total = _match_ft_blendshapes(mesh, ft_definitions[ft_type])
		percent = matched / total
		if(matched > 0 and best_percent < percent):
			best = ft_type
			best_percent = percent
	return best


class AVA_FaceTracking_Blendshapes(STF_ComponentResourceBase):
	ft_type: bpy.props.EnumProperty(items=[("unified_expressions", "Unified Expressions (Preferred)", ""),("arkit", "ARkit", ""),("sranipal", "SRanipal", ""),("facs_reduced", "FACS Reduced (Quest Pro)", ""),("other", "Unknown Tracking Type", "")], name="Type", default="unified_expressions", options=set()) # type: ignore
	ft_type_custom: bpy.props.StringProperty(name="Unknown Tracking Type", options=set()) # type: ignore


class Handler_AVA_FaceTracking_Blendshapes(STF_Handler_Component):
	"""Define face-tracking blendshapes"""
	stf_type = "ava.face_tracking.blendshape"
	stf_category = STF_Category.COMPONENT
	like_types = []
	understood_blender_types = [AVA_FaceTracking_Blendshapes]
	blender_property_name = "ava_face_tracking_blendshape"
	single = True
	filter = [bpy.types.Mesh]
	pretty_name_template = "Face Tracking Blendshapes"

	@classmethod
	def draw(cls, layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_resource: bpy.types.Mesh, component: AVA_FaceTracking_Blendshapes):
		row = layout.row()
		if(bpy.app.version[0] < 5 or bpy.app.version[1] < 2):
			row.operator("wm.url_open", text="VRCFT Documentation", icon="HELP").url = "https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/overview"
			row.operator("wm.url_open", text="Mappings Definition", icon="DOCUMENTS").url = "https://docs.google.com/spreadsheets/d/118jo960co3Mgw8eREFVBsaJ7z0GtKNr52IB4Bz99VTA"
		else:
			row.link(text="VRCFT Documentation", icon="HELP", url="https://docs.vrcft.io/docs/tutorial-avatars/tutorial-avatars-extras/compatibility/overview")
			row.link(text="Mappings Definition", icon="DOCUMENTS", url="https://docs.google.com/spreadsheets/d/118jo960co3Mgw8eREFVBsaJ7z0GtKNr52IB4Bz99VTA")

		layout.use_property_split = True
		layout.label(text="Not all shapes are required, consult the above links to learn more!", icon="INFO")
		layout.prop(component, "ft_type")

		if(component.ft_type != "other"):
			shape_match = _match_ft_blendshapes(context_resource, ft_definitions[component.ft_type])
			split = layout.split(factor=0.4); split.row(); split.label(text=str(shape_match[0]) + " / " + str(shape_match[1]) + " Matched")
		else:
			layout.prop(component, "ft_type_custom")

	@classmethod
	def import_resource(cls, context: STF_ImportContext, json_resource: dict, stf_id: str, context_resource: bpy.types.Mesh) -> Any | STFReport:
		component_ref, component = add_component(context_resource, cls.blender_property_name, stf_id, cls.stf_type)
		import_component_base(context, component, json_resource, cls.blender_property_name, context_resource)
		if("ft_type" in json_resource):
			if(json_resource["ft_type"] in ft_definitions):
				component.ft_type = json_resource["ft_type"]
			else:
				component.ft_type = "other"
				component.ft_type_custom= json_resource["ft_type"]
		return component

	@classmethod
	def export_resource(cls, context: STF_ExportContext, component: AVA_FaceTracking_Blendshapes, context_resource: bpy.types.Mesh) -> tuple[dict, str] | STFReport:
		ret = export_component_base(context, cls.stf_type, component, cls.blender_property_name, context_resource)
		if(component.ft_type != "other"):
			ret["ft_type"] = component.ft_type
		else:
			ret["ft_type"] = component.ft_type_custom
		return ret, component.stf_id


def register():
	setattr(bpy.types.Mesh, Handler_AVA_FaceTracking_Blendshapes.blender_property_name, bpy.props.CollectionProperty(type=AVA_FaceTracking_Blendshapes, options=set()))

def unregister():
	if hasattr(bpy.types.Mesh, Handler_AVA_FaceTracking_Blendshapes.blender_property_name):
		delattr(bpy.types.Mesh, Handler_AVA_FaceTracking_Blendshapes.blender_property_name)
