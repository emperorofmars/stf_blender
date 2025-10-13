
from . import ava_avatar
from . import ava_visemes_blendshape
from . import ava_eyerotation_bone
from . import ava_eyelids_blendshape
from . import ava_secondary_motion
from . import ava_emotes

register_stf_modules = \
	ava_avatar.register_stf_modules + \
	ava_visemes_blendshape.register_stf_modules + \
	ava_eyerotation_bone.register_stf_modules + \
	ava_eyelids_blendshape.register_stf_modules + \
	ava_secondary_motion.register_stf_modules + \
	ava_emotes.register_stf_modules
