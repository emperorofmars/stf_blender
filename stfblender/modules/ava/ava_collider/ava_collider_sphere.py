import bpy
import mathutils

from ....exporter.stf_export_context import STF_ExportContext
from ....importer.stf_import_context import STF_ImportContext
from ....utils.component_utils import STF_BlenderComponentBase, STF_BlenderComponentModule, STF_Component_Ref, add_component, export_component_base, import_component_base
from ....utils.trs_utils import blender_translation_to_stf, stf_translation_to_blender


_stf_type = "ava.collider.sphere"
_blender_property_name = "ava_collider_sphere"


class AVA_Collider_Sphere(STF_BlenderComponentBase):
	radius: bpy.props.FloatProperty(name="Radius", default=1) # type: ignore
	offset_position: bpy.props.FloatVectorProperty(name="Position Offset", size=3, default=(0, 0, 0)) # type: ignore


def _draw_component(layout: bpy.types.UILayout, context: bpy.types.Context, component_ref: STF_Component_Ref, context_object: any, component: AVA_Collider_Sphere):
	layout.prop(component, "radius")
	layout.prop(component, "offset_position")


def _stf_import(context: STF_ImportContext, json_resource: dict, stf_id: str, context_object: any) -> any:
	component_ref, component = add_component(context_object, _blender_property_name, stf_id, _stf_type)
	import_component_base(component, json_resource)
	component.radius = json_resource.get("radius", 1)
	if("offset_position" in json_resource):
		offset_position = mathutils.Vector()
		for index in range(3):
			offset_position[index] = json_resource["offset_position"][index]
		component.offset_position = stf_translation_to_blender(offset_position)
	return component


def _stf_export(context: STF_ExportContext, application_object: AVA_Collider_Sphere, context_object: any) -> tuple[dict, str]:
	ret = export_component_base(_stf_type, application_object)
	ret["radius"] = application_object.radius

	offset_position = mathutils.Vector(application_object.offset_position)
	ret["offset_position"] = blender_translation_to_stf(offset_position)
	return ret, application_object.stf_id


class STF_Module_AVA_Collider_Sphere(STF_BlenderComponentModule):
	stf_type = _stf_type
	stf_kind = "component"
	like_types = ["collider.sphere", "collider"]
	understood_application_types = [AVA_Collider_Sphere]
	import_func = _stf_import
	export_func = _stf_export

	blender_property_name = _blender_property_name
	single = False
	filter = [bpy.types.Object, bpy.types.Bone]
	draw_component_func = _draw_component


register_stf_modules = [
	STF_Module_AVA_Collider_Sphere
]


def register():
	bpy.types.Object.ava_collider_sphere = bpy.props.CollectionProperty(type=AVA_Collider_Sphere) # type: ignore
	bpy.types.Bone.ava_collider_sphere = bpy.props.CollectionProperty(type=AVA_Collider_Sphere) # type: ignore

def unregister():
	if hasattr(bpy.types.Object, "ava_collider_sphere"):
		del bpy.types.Object.ava_collider_sphere
	if hasattr(bpy.types.Bone, "ava_collider_sphere"):
		del bpy.types.Bone.ava_collider_sphere

