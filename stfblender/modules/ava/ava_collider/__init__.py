
from . import ava_collider_sphere, ava_collider_capsule, ava_collider_plane

register_stf_modules = \
	ava_collider_sphere.register_stf_modules + \
	ava_collider_capsule.register_stf_modules + \
	ava_collider_plane.register_stf_modules
