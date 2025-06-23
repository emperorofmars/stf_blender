
from .ava_avatar import ava_avatar
from .ava_visemes_blendshape import ava_visemes_blendshape
from .ava_eyerotation_bone import ava_eyerotation_bone
from .ava_eyelids_blendshape import ava_eyelids_blendshape
from . import ava_collider
from .ava_secondary_motion import ava_secondary_motion
from .ava_emotes import ava_emotes

register_stf_modules = \
	ava_avatar.register_stf_modules + \
	ava_visemes_blendshape.register_stf_modules + \
	ava_eyerotation_bone.register_stf_modules + \
	ava_eyelids_blendshape.register_stf_modules + \
	ava_collider.register_stf_modules + \
	ava_secondary_motion.register_stf_modules + \
	ava_emotes.register_stf_modules
