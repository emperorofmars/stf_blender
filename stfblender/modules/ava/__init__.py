
from .ava_avatar import ava_avatar
from .ava_visemes_blendshape import ava_visemes_blendshape
from .ava_visemes_mapping import ava_visemes_mapping

register_stf_modules = \
	ava_avatar.register_stf_modules + \
	ava_visemes_blendshape.register_stf_modules + \
	ava_visemes_mapping.register_stf_modules
