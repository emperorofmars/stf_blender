import uuid
import bpy

from ....utils.component_utils import add_component
from ..ava_avatar import STF_Module_AVA_Avatar, AVA_Avatar
from ..ava_visemes_blendshape import STF_Module_AVA_Visemes_Blendshape, automap as automap_visemes
from ..ava_eyelids_blendshape import STF_Module_AVA_Eyelids_Blendshape, automap as automap_eyelids
from ..ava_facial_tracking_blendshape.ava_face_tracking_blendshape import STF_Module_AVA_FaceTracking_Blendshapes, automap as automap_ft
from ..ava_eyerotation_bone import STF_Module_AVA_EyeRotation_Bone
from ...expanded.stfexp_armature_humanoid import HumanoidBone, STF_Module_STFEXP_Armature_Humanoid, STFEXP_Armature_Humanoid, _map_humanoid_bones as automap_humanoid


def detect_mesh_and_armature(collection: bpy.types.Collection) -> tuple[bpy.types.Object, bpy.types.Object]:
	main_mesh = None
	main_armature = None
	for object in collection.all_objects[:]:
		if(type(object.data) == bpy.types.Mesh and ("body" in object.name.lower() or "face" in object.name.lower())):
			if(not main_mesh or len(object.name) < len(main_mesh.name)):
				main_mesh = object
	for object in collection.all_objects[:]:
		if(type(object.data) == bpy.types.Armature and ("armature" in object.name.lower() or "skeleton" in object.name.lower())):
			if(not main_armature or len(object.name) < len(main_armature.name)):
				main_armature = object
	return main_mesh, main_armature


def clear_components(target: bpy.types.ID, component_property: str):
	for preexisting in getattr(target, component_property):
		for ref_index, ref in enumerate(target.stf_info.stf_components):
			if(ref.stf_id == preexisting.stf_id):
				target.stf_info.stf_components.remove(ref_index)
				break
	getattr(target, component_property).clear()


def ava_autosetup(target: bpy.types.Collection):
	main_mesh, main_armature = detect_mesh_and_armature(target)
	if(not main_mesh or not main_armature):
		return

	target.stf_use_collection_as_prefab = True

	# Clear existing components
	clear_components(target, STF_Module_AVA_Avatar.blender_property_name)
	clear_components(main_armature.data, STF_Module_STFEXP_Armature_Humanoid.blender_property_name)
	clear_components(main_armature.data, STF_Module_AVA_EyeRotation_Bone.blender_property_name)
	clear_components(main_mesh.data, STF_Module_AVA_Visemes_Blendshape.blender_property_name)
	clear_components(main_mesh.data, STF_Module_AVA_Eyelids_Blendshape.blender_property_name)
	clear_components(main_mesh.data, STF_Module_AVA_FaceTracking_Blendshapes.blender_property_name)

	# Apply
	_, avatar = add_component(target, STF_Module_AVA_Avatar.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_Avatar.stf_type)
	avatar: AVA_Avatar = avatar # autocomplete
	avatar.name = target.name
	avatar.primary_mesh_instance = main_mesh
	avatar.primary_armature_instance = main_armature

	_, humanoid = add_component(main_armature.data, STF_Module_STFEXP_Armature_Humanoid.blender_property_name, str(uuid.uuid4()), STF_Module_STFEXP_Armature_Humanoid.stf_type)
	humanoid: STFEXP_Armature_Humanoid  = humanoid
	automap_humanoid(humanoid, main_armature.data)

	eye_l = humanoid.bone_mappings["eye.l"].bone if "eye.l" in humanoid.bone_mappings else None
	eye_r = humanoid.bone_mappings["eye.r"].bone if "eye.r" in humanoid.bone_mappings else None
	if(eye_l and eye_r):
		viewport_loc = (main_armature.pose.bones[eye_l].matrix.decompose()[0] + main_armature.pose.bones[eye_r].matrix.decompose()[0]) / 2
		if("$ViewportFirstPerson" in bpy.data.objects):
			viewport_object = bpy.data.objects["$ViewportFirstPerson"]
		else:
			viewport_object = bpy.data.objects.new("$ViewportFirstPerson", None)
			viewport_object.empty_display_size = 0.1
			viewport_object.empty_display_type = "SINGLE_ARROW"
			target.objects.link(viewport_object)
		viewport_object.location = viewport_loc
		avatar.viewport = viewport_object

	_, eyerotation = add_component(main_armature.data, STF_Module_AVA_EyeRotation_Bone.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_EyeRotation_Bone.stf_type)

	_, visemes = add_component(main_mesh.data, STF_Module_AVA_Visemes_Blendshape.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_Visemes_Blendshape.stf_type)
	automap_visemes(visemes, main_mesh.data)

	_, eyelids = add_component(main_mesh.data, STF_Module_AVA_Eyelids_Blendshape.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_Eyelids_Blendshape.stf_type)
	automap_eyelids(eyelids, main_mesh.data)

	ft_match = automap_ft(main_mesh.data)
	if(ft_match):
		_, facetracking = add_component(main_mesh.data, STF_Module_AVA_FaceTracking_Blendshapes.blender_property_name, str(uuid.uuid4()), STF_Module_AVA_FaceTracking_Blendshapes.stf_type)
		facetracking.ft_type = ft_match

