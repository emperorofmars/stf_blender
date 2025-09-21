
from . import stfexp_mesh_seams
from . import stfexp_mesh_creases
from . import stfexp_armature_humanoid
from . import stfexp_constraint_twist
from . import stfexp_lightprobe_anchor

register_stf_modules = \
	stfexp_mesh_seams.register_stf_modules + \
	stfexp_mesh_creases.register_stf_modules + \
	stfexp_armature_humanoid.register_stf_modules + \
	stfexp_constraint_twist.register_stf_modules + \
	stfexp_lightprobe_anchor.register_stf_modules
