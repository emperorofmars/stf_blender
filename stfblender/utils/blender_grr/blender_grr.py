import bpy

from .stf_data_resource_reference import STFDataResourceReference, draw_stf_data_resource_reference, resolve_stf_data_resource_reference, validate_stf_data_resource_reference
from .blender_resource_reference import BlenderResourceReference, draw_blender_resource_reference, resolve_blender_resource_reference, validate_blender_resource_reference
from ...base.stf_module_data import STF_BlenderDataResourceBase
from ...base.stf_module_component import STF_BlenderComponentBase
from ...utils.armature_bone import ArmatureBone

"""
Blender Generic Resource Reference

Bringing polymorphism to Blender

This is a big TODO, making this complete, user friendly and nice to handle will take effort.
"""

reference_type_values = (
	("blender", "Blender Native Resource", "Objects, Meshes, Armatures, etc.."),
	("stf_data_resource", "STF Resource", "STF Resources not natively supported by Blender"),
	("stf_component", "STF Component", "STF Components on a native Blender or STF-Data Resource"),
)
component_reference_type_values = (
	("blender", "Blender Native Resource", "Objects, Meshes, Armatures, etc.."),
	("stf_data_resource", "STF Resource", "STF Resources not natively supported by Blender"),
)

class BlenderGRR(bpy.types.PropertyGroup):
	reference_type: bpy.props.EnumProperty(name="Reference Type", items=reference_type_values) # type: ignore

	blender_resource_reference: bpy.props.PointerProperty(type=BlenderResourceReference, name="Blender Resource Reference") # type: ignore
	stf_data_resource_reference: bpy.props.PointerProperty(type=STFDataResourceReference, name="STF Data-Resource Reference") # type: ignore

	component_reference_type: bpy.props.EnumProperty(name="Component From", items=component_reference_type_values) # type: ignore
	stf_component_id: bpy.props.StringProperty(name="Component ID") # type: ignore


def draw_blender_grr(layout: bpy.types.UILayout, grr: BlenderGRR):
	layout.prop(grr, "reference_type")

	match(grr.reference_type):
		case "blender": draw_blender_resource_reference(layout, grr.blender_resource_reference)
		case "stf_data_resource": draw_stf_data_resource_reference(layout, grr.stf_data_resource_reference)
		case "stf_component":
			layout.prop(grr, "component_reference_type")
			match(grr.component_reference_type):
				case "blender":
					draw_blender_resource_reference(layout, grr.blender_resource_reference)
					component_holder = resolve_blender_resource_reference(grr.blender_resource_reference)
					if(component_holder and hasattr(component_holder, "stf_info")):
						layout.prop_search(grr, "stf_component_id", component_holder.stf_info, "stf_components", icon="ERROR" if not grr.stf_component_id or grr.stf_component_id not in component_holder.stf_info.stf_components else "NONE")

						if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_info.stf_components):
							component_ref = component_holder.stf_info.stf_components[grr.stf_component_id]
							# let component
							for component in getattr(component_holder, component_ref.blender_property_name):
								if(component.stf_id == grr.stf_component_id):
									break
							split = layout.split(factor=0.4)
							row = split.row()
							if(layout.use_property_split):
								row.alignment = "RIGHT"
							row.label(text="Type   ")
							split.label(text=component_ref.stf_type)
							if(component):
								split = layout.split(factor=0.4)
								row = split.row()
								if(layout.use_property_split):
									row.alignment = "RIGHT"
								row.label(text="Name   ")
								split.label(text=component.stf_name)

				case "stf_data_resource":
					draw_stf_data_resource_reference(layout, grr.stf_data_resource_reference)
					component_holder_ret = resolve_stf_data_resource_reference(grr.stf_data_resource_reference)
					if(component_holder_ret):
						_, component_holder = component_holder_ret
						layout.prop_search(grr, "stf_component_id", component_holder, "stf_components", icon="ERROR" if not grr.stf_component_id or grr.stf_component_id not in component_holder.stf_components else "NONE")

						if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_components):
							component_ref = component_holder.stf_components[grr.stf_component_id]
							# let component
							for component in getattr(component_holder.id_data, component_ref.blender_property_name):
								if(component.stf_id == grr.stf_component_id):
									break
							split = layout.split(factor=0.4)
							row = split.row()
							if(layout.use_property_split):
								row.alignment = "RIGHT"
							row.label(text="Type   ")
							split.label(text=component_ref.stf_type)
							if(component):
								split = layout.split(factor=0.4)
								row = split.row()
								if(layout.use_property_split):
									row.alignment = "RIGHT"
								row.label(text="Name   ")
								split.label(text=component.stf_name)


def resolve_blender_grr(grr: BlenderGRR) -> any:
	match(grr.reference_type):
		case "blender": return resolve_blender_resource_reference(grr.blender_resource_reference)
		case "stf_data_resource":
			ret = resolve_stf_data_resource_reference(grr.stf_data_resource_reference)
			if(ret):
				return ret[1]
		case "stf_component":
			match(grr.component_reference_type):
				case "blender":
					component_holder = resolve_blender_resource_reference(grr.blender_resource_reference)
					if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_info.stf_components):
						component_ref = component_holder.stf_info.stf_components[grr.stf_component_id]
						for component in getattr(component_holder, component_ref.blender_property_name):
							if(component.stf_id == grr.stf_component_id):
								return component
				case "stf_data_resource":
					component_holder_ret = resolve_stf_data_resource_reference(grr.stf_data_resource_reference)
					if(component_holder_ret):
						_, component_holder = component_holder_ret
						if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_components):
							component_ref = component_holder.stf_components[grr.stf_component_id]
							for component in getattr(component_holder.id_data, component_ref.blender_property_name):
								if(component.stf_id == grr.stf_component_id):
									return component
	return None


def construct_blender_grr(generic_resource: any, grr: BlenderGRR):
	print(type(generic_resource), " : ", isinstance(generic_resource, bpy.types.ID), " - ", isinstance(generic_resource, STF_BlenderComponentBase))

	if(isinstance(generic_resource, bpy.types.ID)):
		grr.reference_type = "blender"
		grr.blender_resource_reference.blender_type = generic_resource.id_type
		grr.blender_resource_reference[generic_resource.id_type.lower()] = generic_resource
	if(isinstance(generic_resource, ArmatureBone)):
		grr.reference_type = "blender"
		grr.blender_resource_reference.blender_type = "ARMATURE"
		grr.blender_resource_reference.armature = generic_resource.armature
		grr.blender_resource_reference.bone_name = generic_resource.get_bone().name
	elif(isinstance(generic_resource, STF_BlenderDataResourceBase)):
		grr.reference_type = "stf_data_resource"
		# todo
	elif(isinstance(generic_resource, STF_BlenderComponentBase)):
		grr.reference_type = "stf_component"
		# todo

	return


def validate_blender_grr(grr: BlenderGRR) -> bool:
	if(not grr):
		return False
	match(grr.reference_type):
		case "blender": return validate_blender_resource_reference(grr.blender_resource_reference)
		case "stf_data_resource": return validate_stf_data_resource_reference(grr.stf_data_resource_reference)
		case "stf_component": pass
	return False
