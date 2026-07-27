
"""
STF resources that specify functionality of humanoid avatars, useful for VR and V-Tubing.
"""

from .ava_avatar import Handler_AVA_Avatar
from .ava_voice_position import Handler_AVA_VoicePosition
from .ava_visemes_blendshape import Handler_AVA_Visemes_Blendshape
from .ava_eyerotation_bone import Handler_AVA_EyeRotation_Bone
from .ava_eyelids_blendshape import Handler_AVA_Eyelids_Blendshape
from .ava_secondary_motion import Handler_AVA_SecondaryMotion
from .ava_expressions import Handler_AVA_Expressions
from .ava_facial_tracking_blendshape.ava_face_tracking_blendshape import Handler_AVA_FaceTracking_Blendshapes

__all__ = ["register_stf_handlers"]

register_stf_handlers = [
	Handler_AVA_Avatar,
	Handler_AVA_VoicePosition,
	Handler_AVA_Visemes_Blendshape,
	Handler_AVA_EyeRotation_Bone,
	Handler_AVA_Eyelids_Blendshape,
	Handler_AVA_SecondaryMotion,
	Handler_AVA_Expressions,
	Handler_AVA_FaceTracking_Blendshapes,
]
