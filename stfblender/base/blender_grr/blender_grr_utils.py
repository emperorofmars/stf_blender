import bpy

from .blender_grr import BlenderGRR
from .stf_data_resource_reference_utils import draw_stf_data_resource_reference, resolve_stf_data_resource_reference, validate_stf_data_resource_reference
from .blender_resource_reference import draw_blender_resource_reference, pretty_print_blender_resource_reference, resolve_blender_resource_reference, validate_blender_resource_reference
from ...base.stf_module_data import STF_BlenderDataResourceBase, STF_Data_Ref
from ...base.stf_module_component import STF_BlenderComponentBase, STF_Component_Ref
from ...utils.armature_bone import ArmatureBone
from .utils import draw_component_info

"""
Blender Generic Resource Reference

Bringing polymorphism to Blender

It works right now, however making this actually user friendly and nice to handle will take some more effort.
"""

def pretty_print_blender_grr(grr: BlenderGRR) -> str:
	match(grr.reference_type):
		case "blender": return pretty_print_blender_resource_reference(grr.blender_resource_reference)
		case "stf_data_resource": return "foo"
		case "stf_component": return "bar"


def draw_blender_grr(layout: bpy.types.UILayout, grr: BlenderGRR, reference_type_filter: str = None):
	if(not reference_type_filter):
		layout.prop(grr, "reference_type")

	match(grr.reference_type):
		case "blender":
			if(not reference_type_filter or reference_type_filter == "blender"):
				draw_blender_resource_reference(layout, grr.blender_resource_reference)
		case "stf_data_resource":
			if(not reference_type_filter or reference_type_filter == "stf_data_resource"):
				draw_stf_data_resource_reference(layout, grr.stf_data_resource_reference)
		case "stf_component":
			if(not reference_type_filter or reference_type_filter == "stf_component"):
				layout.prop(grr, "component_reference_type")

				match(grr.component_reference_type):
					case "blender":
						draw_blender_resource_reference(layout, grr.blender_resource_reference)
						component_holder = resolve_blender_resource_reference(grr.blender_resource_reference)
						if(component_holder and hasattr(component_holder, "stf_info")):
							layout.prop_search(grr, "stf_component_id", component_holder.stf_info, "stf_components", icon="ERROR" if not grr.stf_component_id or grr.stf_component_id not in component_holder.stf_info.stf_components else "NONE")

							if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_info.stf_components):
								draw_component_info(layout, component_holder, component_holder.stf_info, grr.stf_component_id)

					case "stf_data_resource":
						draw_stf_data_resource_reference(layout, grr.stf_data_resource_reference)
						component_holder_ret = resolve_stf_data_resource_reference(grr.stf_data_resource_reference)
						if(component_holder_ret):
							_, component_holder = component_holder_ret
							layout.prop_search(grr, "stf_component_id", component_holder, "stf_components", icon="ERROR" if not grr.stf_component_id or grr.stf_component_id not in component_holder.stf_components else "NONE")

							if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_components):
								draw_component_info(layout, component_holder, component_holder.stf_info, grr.stf_component_id)


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
					if(component_holder and grr.stf_component_id and grr.stf_component_id in component_holder.stf_info.stf_components):
						component_ref: STF_Component_Ref = component_holder.stf_info.stf_components[grr.stf_component_id]
						for component in getattr(component_holder, component_ref.blender_property_name):
							if(component.stf_id == grr.stf_component_id):
								return component
				case "stf_data_resource":
					component_holder_ret = resolve_stf_data_resource_reference(grr.stf_data_resource_reference)
					if(component_holder_ret):
						_, component_holder = component_holder_ret
						if(grr.stf_component_id and grr.stf_component_id in component_holder.stf_components):
							component_ref: STF_Component_Ref = component_holder.stf_components[grr.stf_component_id]
							for component in getattr(component_holder.id_data, component_ref.blender_property_name):
								if(component.stf_id == grr.stf_component_id):
									return component
	return None


def construct_blender_grr(generic_resource: any, grr: BlenderGRR, force_resource_id: str = None):
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
		grr.stf_data_resource_reference.collection = generic_resource.id_data
		grr.stf_data_resource_reference.stf_data_resource_id = generic_resource.stf_id
	elif(isinstance(generic_resource, STF_BlenderComponentBase)):
		grr.reference_type = "stf_component"
		target_id = force_resource_id if force_resource_id else generic_resource.stf_id
		# try if component sits on a stf-data-resource
		if(type(generic_resource.id_data) == bpy.types.Collection):
			for data_resource_ref in generic_resource.id_data.stf_data_refs:
				data_resource_ref: STF_Data_Ref = data_resource_ref
				for data_resource in getattr(generic_resource.id_data, data_resource_ref.blender_property_name):
					for component_ref in data_resource.stf_components:
						if(component_ref.stf_id == target_id):
							grr.component_reference_type = "stf_data_resource"
							grr.stf_data_resource_reference.collection = generic_resource.id_data
							grr.stf_data_resource_reference.stf_data_resource_id = data_resource_ref.stf_id
							grr.stf_component_id = target_id
							return
		# else component sits on a blender native resource
		grr.component_reference_type = "blender"
		grr.blender_resource_reference.blender_type = generic_resource.id_data.id_type
		grr.blender_resource_reference[generic_resource.id_data.id_type.lower()] = generic_resource.id_data
		# if the id_data this component sits on is an armature, it can be referenced by one of its bones
		if(type(generic_resource.id_data) == bpy.types.Armature):
			for bone in generic_resource.id_data.bones:
				for component_ref in bone.stf_info.stf_components:
					if(component_ref.stf_id == target_id):
						grr.blender_resource_reference.bone_name = bone.name
						break
		grr.stf_component_id = target_id
	return


def validate_blender_grr(grr: BlenderGRR) -> bool:
	if(not grr):
		return False
	match(grr.reference_type):
		case "blender": return validate_blender_resource_reference(grr.blender_resource_reference)
		case "stf_data_resource": return validate_stf_data_resource_reference(grr.stf_data_resource_reference)
		case "stf_component": return True # todo
	return False
