
from .ava_avatar import ava_avatar
from .ava_visemes_blendshape import ava_visemes_blendshape
from .ava_eyerotation_bone import ava_eyerotation_bone
from .ava_eyelids_blendshape import ava_eyelids_blendshape

register_stf_modules = \
	ava_avatar.register_stf_modules + \
	ava_visemes_blendshape.register_stf_modules + \
	ava_eyerotation_bone.register_stf_modules + \
	ava_eyelids_blendshape.register_stf_modules
