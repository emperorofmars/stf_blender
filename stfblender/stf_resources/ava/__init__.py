
"""
STF resources that specify functionality of humanoid avatars, useful for VR and V-Tubing.
"""

from .ava_avatar import Handler_AVA_Avatar
from .ava_voice_position import Handler_AVA_VoicePosition
from .ava_visemes_blendshape import Handler_AVA_Visemes_Blendshape
from . import ava_eyerotation_bone
from . import ava_eyelids_blendshape
from . import ava_secondary_motion
from .ava_expressions import Handler_AVA_Expressions
from .ava_facial_tracking_blendshape import ava_face_tracking_blendshape

register_stf_handlers = [
	Handler_AVA_Avatar,
	Handler_AVA_VoicePosition,
	Handler_AVA_Visemes_Blendshape,

	Handler_AVA_Expressions,
] + \
	ava_eyerotation_bone.register_stf_handlers + \
	ava_eyelids_blendshape.register_stf_handlers + \
	ava_secondary_motion.register_stf_handlers + \
	ava_face_tracking_blendshape.register_stf_handlers
