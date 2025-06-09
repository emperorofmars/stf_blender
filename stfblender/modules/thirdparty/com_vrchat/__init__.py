
from .vrc_avatar_colliders import vrc_avatar_colliders
from .vrc_physbone import vrc_physbone

register_stf_modules = \
	vrc_avatar_colliders.register_stf_modules + \
	vrc_physbone.register_stf_modules
