
from .ava import ava_avatar
from .ava import ava_constraint_twist

register_stf_modules = ava_avatar.register_stf_modules + ava_constraint_twist.register_stf_modules
