import bpy

from .stf_module_component import STF_Component_Ref

"""
Blender Generic Resource Reference

Bringing polymorphism to Blender
"""

reference_type_values = (
	("blender", "Blender Native Resource", ""),
	("stf_component", "STF Component on Blender Resource", ""),
	("stf_data_resource", "STF Data Resource", ""),
	("stf_data_resource_component", "STF Component on STF Data Resource", ""),
)

blender_type_values = (
	("ACTION","ACTION",""),
	("ARMATURE","ARMATURE",""),
	("BRUSH","BRUSH",""),
	("CACHEFILE","CACHEFILE",""),
	("CAMERA","CAMERA",""),
	("COLLECTION","COLLECTION",""),
	("CURVE","CURVE",""),
	("CURVES","CURVES",""),
	("FONT","FONT",""),
	("GREASEPENCIL","GREASEPENCIL",""),
	("GREASEPENCIL_V3","GREASEPENCIL_V3",""),
	("IMAGE","IMAGE",""),
	("KEY","KEY",""),
	("LATTICE","LATTICE",""),
	("LIBRARY","LIBRARY",""),
	("LIGHT","LIGHT",""),
	("LIGHT_PROBE","LIGHT_PROBE",""),
	("LINESTYLE","LINESTYLE",""),
	("MASK","MASK",""),
	("MATERIAL","MATERIAL",""),
	("MESH","MESH",""),
	("META","META",""),
	("MOVIECLIP","MOVIECLIP",""),
	("NODETREE","NODETREE",""),
	("OBJECT","OBJECT",""),
	("PAINTCURVE","PAINTCURVE",""),
	("PALETTE","PALETTE",""),
	("PARTICLE","PARTICLE",""),
	("POINTCLOUD","POINTCLOUD",""),
	#("SCENE","SCENE",""),
	("SCREEN","SCREEN",""),
	("SOUND","SOUND",""),
	("SPEAKER","SPEAKER",""),
	("TEXT","TEXT",""),
	("TEXTURE","TEXTURE",""),
	("VOLUME","VOLUME",""),
	("WINDOWMANAGER","WINDOWMANAGER",""),
	("WORKSPACE","WORKSPACE",""),
	("WORLD","WORLD",""),
)


class BlenderGRR(bpy.types.PropertyGroup):
	reference_type: bpy.props.EnumProperty(name="Reference Type", items=reference_type_values) # type: ignore
	blender_type: bpy.props.EnumProperty(name="Type", items=blender_type_values) # type: ignore

	use_scene_collection: bpy.props.BoolProperty(default=False, name="Use Scene Collection") # type: ignore
	scene: bpy.props.PointerProperty(type=bpy.types.Scene, name="Scene") # type: ignore
	collection: bpy.props.PointerProperty(type=bpy.types.Collection, name="Collection") # type: ignore
	object: bpy.props.PointerProperty(type=bpy.types.Object, name="Object") # type: ignore

	stf_data_resource_id: bpy.props.StringProperty(name="Resource ID") # type: ignore
	stf_component_id: bpy.props.StringProperty(name="Component ID") # type: ignore


def __draw_blender_collection_selection(layout: bpy.types.UILayout, grr: BlenderGRR) -> bool:
	layout.prop(grr, "use_scene_collection")
	if(not grr.use_scene_collection):
		layout.prop(grr, "collection")
		return bool(grr.collection)
	else:
		layout.prop(grr, "scene")
		return bool(grr.scene)


def __draw_blender_type_selection(layout: bpy.types.UILayout, grr: BlenderGRR) -> bool:
	layout.prop(grr, "blender_type")
	if(grr.blender_type == "COLLECTION"):
		return __draw_blender_collection_selection(layout, grr)
	elif(grr.blender_type == "OBJECT"):
		layout.prop(grr, "object")
		return bool(grr.object)

	# todo everything else
	return False


def draw_blender_grr(layout: bpy.types.UILayout, grr: BlenderGRR):
	layout.prop(grr, "reference_type")

	if(grr.reference_type == "stf_component"):
		if(__draw_blender_type_selection(layout, grr)):
			layout.prop(grr, "stf_component_id")
	elif(grr.reference_type == "stf_data_resource"):
		if(__draw_blender_collection_selection(layout, grr)):
			layout.prop(grr, "stf_data_resource_id")
	elif(grr.reference_type == "stf_data_resource_component"):
		if(__draw_blender_collection_selection(layout, grr)):
			layout.prop(grr, "stf_data_resource_id")
			if(grr.stf_data_resource_id):
				layout.prop(grr, "stf_component_id")


def __get_blender_property(holder: any, ref_holder: any, property_holder: any, target_id: str):
	for resource_ref in ref_holder:
		if(resource_ref.stf_id == target_id):
			for resource in getattr(property_holder, resource_ref.blender_property_name):
				if(resource.stf_id == resource_ref.stf_id):
					return resource
	return None


def resolve_blender_grr(grr: BlenderGRR) -> any:
	if(grr.reference_type == "blender"):
		pass # todo return the resource based on the blender_type
	elif(grr.reference_type == "stf_component"):
		pass
	elif(grr.reference_type == "stf_data_resource"):
		if(grr.use_scene_collection and grr.scene):
			return __get_blender_property(grr.scene.collection, grr.scene.collection.stf_data_refs, grr.scene.collection, grr.stf_data_resource_id)
		elif(grr.collection):
			return __get_blender_property(grr.collection, grr.collection.stf_data_refs, grr.collection, grr.stf_data_resource_id)
	elif(grr.reference_type == "stf_data_resource_component"):
		pass
	return None

