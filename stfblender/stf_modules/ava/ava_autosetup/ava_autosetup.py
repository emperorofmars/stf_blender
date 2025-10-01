import uuid
import bpy

from ....utils.component_utils import add_component
from ..ava_avatar import STF_Module_AVA_Avatar, AVA_Avatar


def ava_autosetup(target: bpy.types.Collection):
	# Check
	# todo

	target.stf_use_collection_as_prefab = True

	# Remove preexisting setup
	for preexisting in getattr(target, STF_Module_AVA_Avatar.blender_property_name):
		# let ref_index
		for ref_index, ref in enumerate(target.stf_info.stf_components):
			if(ref.stf_id == preexisting.stf_id):
				break
		else:
			continue
		target.stf_info.stf_components.remove(ref_index)
	getattr(target, STF_Module_AVA_Avatar.blender_property_name).clear()


	# Apply
	_, avatar = add_component(target, STF_Module_AVA_Avatar.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_Avatar.stf_type)
	avatar: AVA_Avatar = avatar # autocomplete

	avatar.name = target.name

	# todo 

