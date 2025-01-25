
from . import ava_avatar
from . import ava_constraint_twist
from . import ava_armature_humanoid

register_stf_modules = \
	ava_avatar.register_stf_modules \
	+ ava_constraint_twist.register_stf_modules \
	+ ava_armature_humanoid.register_stf_modules
