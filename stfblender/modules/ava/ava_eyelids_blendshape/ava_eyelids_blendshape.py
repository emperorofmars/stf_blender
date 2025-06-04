import bpy

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base


_stf_type = "ava.eyelids.blendshape"
_blender_property_name = "ava_eyelids_blendshape"


_eyelid_prefixes = ["", "vis.", "vis_", "vis ", "vrc.", "vrc_", "vrc ", "eye", "eyes", "eyelid", "eyelids"]
_eyelid_shapes = {
	"closed": ["close", "closed", "blink"],
	"up": ["up", "lookup", "look up", "look_up"],
	"down": ["down", "lookdown", "look down", "look_down"],
	"left": ["right", "lookright", "look right", "right_right"],
	"right": [".r", ".right", "_r", "_right", " right"]
}
_eyelid_suffixes_left = [".l", ".left", "_l", "_left", " left", "left"]
_eyelid_suffixes_right = [".r", ".right", "_r", "_right", " right", "right"]


def _map_blendshape(blendshape_name: str) -> str:
	for prefix in _eyelid_prefixes:
		for shape_name, shape_mappings in _eyelid_shapes.items():
			for shape in shape_mappings:
				if(blendshape_name.lower() == prefix + shape):
					return "eyes_closed" if shape_name == "closed" else "look_" + shape_name
				else:
					for suffix_left in _eyelid_suffixes_left:
						if(blendshape_name.lower() == prefix + shape + suffix_left):
							return "eye_closed_left" if shape_name == "closed" else "look_" + shape_name + "_left"
					for suffix_right in _eyelid_suffixes_right:
						if(blendshape_name.lower() == prefix + shape + suffix_right):
							return "eye_closed_right" if shape_name == "closed" else "look_" + shape_name + "_right"


class AutomapEyelids(bpy.types.Operator):
	"""Map from Names"""
	bl_idname = "ava.ava_map_blendshape_eyelids"
	bl_label = "Map from Names"
	bl_options = {"REGISTER", "UNDO"}

	component_id: bpy.props.StringProperty() # type: ignore

	def execute(self, context):
		for component in context.mesh.ava_eyelids_blendshape:
			if(component.stf_id == self.component_id):
				break

		if(context.mesh.shape_keys):
			for blendshape_name in context.mesh.shape_keys.key_blocks:
				mapping = _map_blendshape(blendshape_name.name)
				if(mapping and (not getattr(component, mapping) or len(getattr(component, mapping)) > len(blendshape_name.name))):
					setattr(component, mapping, blendshape_name.name)

		return {"FINISHED"}


class AVA_Eyelids_Blendshape(STF_BlenderComponentBase):
	eyes_closed: bpy.props.StringProperty(name="Both Closed") # type: ignore
	look_up: bpy.props.StringProperty(name="Both Up") # type: ignore
	look_down: bpy.props.StringProperty(name="Both Down") # type: ignore
	look_left: bpy.props.StringProperty(name="Both Left") # type: ignore
	look_right: bpy.props.StringProperty(name="Both Right") # type: ignore

	eye_closed_left: bpy.props.StringProperty(name="Left Closed") # type: ignore
	look_up_left: bpy.props.StringProperty(name="Left Up") # type: ignore
	look_down_left: bpy.props.StringProperty(name="Left Down") # type: ignore
	look_left_left: bpy.props.StringProperty(name="Left Left") # type: ignore
	look_right_left: bpy.props.StringProperty(name="Left Right") # type: ignore

	eye_closed_right: bpy.props.StringProperty(name="Right Closed") # type: ignore
	look_up_right: bpy.props.StringProperty(name="Right Up") # type: ignore
	look_down_right: bpy.props.StringProperty(name="Right Down") # type: ignore
	look_left_right: bpy.props.StringProperty(name="Right Left") # type: ignore
	look_right_right: bpy.props.StringProperty(name="Right Right") # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, parent_application_object: any, component: AVA_Eyelids_Blendshape):
	layout.operator(AutomapEyelids.bl_idname).component_id = component.stf_id

	layout.prop(component, "eyes_closed")
	layout.prop(component, "look_up")
	layout.prop(component, "look_down")
	layout.prop(component, "look_left")
	layout.prop(component, "look_right")

	layout.separator(factor=1)

	layout.prop(component, "eye_closed_left")
	layout.prop(component, "look_up_left")
	layout.prop(component, "look_down_left")
	layout.prop(component, "look_left_left")
	layout.prop(component, "look_right_left")
	
	layout.separator(factor=1)

	layout.prop(component, "eye_closed_right")
	layout.prop(component, "look_up_right")
	layout.prop(component, "look_down_right")
	layout.prop(component, "look_left_right")
	layout.prop(component, "look_right_right")


def _stf_import(context: STF_ImportContext, json_resource: dict, id: str, parent_application_object: any) -> any:
	component_ref, component = add_component(parent_application_object, _blender_property_name, id, _stf_type)
	import_component_base(component, json_resource)

	for shape_name, _ in _eyelid_shapes.items():
		if(shape_name in json_resource):
			setattr(component, "eyes_closed" if shape_name == "closed" else "look_" + shape_name, json_resource[shape_name])

	for shape_name, _ in _eyelid_shapes.items():
		if(shape_name + "_left" in json_resource):
			setattr(component, "eye_closed_left" if shape_name == "closed" else "look_" + shape_name + "_left", json_resource[shape_name + "_left"])

	for shape_name, _ in _eyelid_shapes.items():
		if(shape_name + "_right" in json_resource):
			setattr(component, "eye_closed_right" if shape_name == "closed" else "look_" + shape_name + "_right", json_resource[shape_name + "_right"])

	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Eyelids_Blendshape, parent_application_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)

	for shape_name, _ in _eyelid_shapes.items():
		ret[shape_name] = getattr(application_object, "eyes_closed" if shape_name == "closed" else "look_" + shape_name)

	for shape_name, _ in _eyelid_shapes.items():
		ret[shape_name + "_left"] = getattr(application_object, "eye_closed_left" if shape_name == "closed" else "look_" + shape_name + "_left")

	for shape_name, _ in _eyelid_shapes.items():
		ret[shape_name + "_right"] = getattr(application_object, "eye_closed_right" if shape_name == "closed" else "look_" + shape_name + "_right")

	return ret, application_object.stf_id


class STF_Module_AVA_Eyelids_Blendshape(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	understood_application_types = [AVA_Eyelids_Blendshape]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = True
	filter = [bpy.types.Mesh]
	draw_component_func = _draw_component

	like_types = []


register_stf_modules = [
	STF_Module_AVA_Eyelids_Blendshape
]


def register():
	bpy.types.Mesh.ava_eyelids_blendshape = bpy.props.CollectionProperty(type=AVA_Eyelids_Blendshape) # type: ignore

def unregister():
	if hasattr(bpy.types.Mesh, "ava_eyelids_blendshape"):
		del bpy.types.Mesh.ava_eyelids_blendshape

