
from . import stfexp_mesh_seams
from . import stfexp_mesh_creases
from . import stfexp_armature_humanoid
from . import stfexp_constraint_twist
from . import stfexp_lightprobe_anchor
from . import stfexp_collider_sphere
from . import stfexp_collider_capsule
from . import stfexp_collider_plane
from . import stfexp_camera
from . import stfexp_light

register_stf_modules = \
	stfexp_mesh_seams.register_stf_modules + \
	stfexp_mesh_creases.register_stf_modules + \
	stfexp_armature_humanoid.register_stf_modules + \
	stfexp_constraint_twist.register_stf_modules + \
	stfexp_lightprobe_anchor.register_stf_modules + \
	stfexp_collider_sphere.register_stf_modules + \
	stfexp_collider_capsule.register_stf_modules + \
	stfexp_collider_plane.register_stf_modules + \
	stfexp_camera.register_stf_modules + \
	stfexp_light.register_stf_modules
