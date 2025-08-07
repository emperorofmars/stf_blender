
from .stfexp_mesh_seams import stfexp_mesh_seams
from .stfexp_mesh_creases import stfexp_mesh_creases
from .stfexp_armature_humanoid import stfexp_armature_humanoid
from .stfexp_constraint_twist import stfexp_constraint_twist
from .stfexp_lightprobe_anchor import stfexp_lightprobe_anchor

register_stf_modules = \
	stfexp_mesh_seams.register_stf_modules + \
	stfexp_mesh_creases.register_stf_modules + \
	stfexp_armature_humanoid.register_stf_modules + \
	stfexp_constraint_twist.register_stf_modules + \
	stfexp_lightprobe_anchor.register_stf_modules
