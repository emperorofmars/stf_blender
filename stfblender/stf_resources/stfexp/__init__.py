
"""
Expanded STF resources that provide additional functionality.

May not be supported by every STF implementation fully.
"""

from . import stfexp_mesh_seams
from . import stfexp_mesh_creases
from . import stfexp_armature_humanoid
from . import stfexp_constraint_twist
from . import stfexp_constraint_rotation
from . import stfexp_constraint_parent
from . import stfexp_constraint_ik
from . import stfexp_lightprobe_anchor
from . import stfexp_collider_sphere
from . import stfexp_collider_capsule
from . import stfexp_collider_plane
from . import stfexp_camera
from . import stfexp_light
from .stfexp_text.stfexp_text import Handler_STFEXP_Text
from . import stfexp_instance_text
from .stfexp_animation_blendtree import Handler_STFEXP_Animation_Blendtree
from . import stfexp_node_ethereal

register_stf_handlers = [
	Handler_STFEXP_Text,
	Handler_STFEXP_Animation_Blendtree,
] + \
	stfexp_mesh_seams.register_stf_handlers + \
	stfexp_mesh_creases.register_stf_handlers + \
	stfexp_armature_humanoid.register_stf_handlers + \
	stfexp_constraint_twist.register_stf_handlers + \
	stfexp_constraint_rotation.register_stf_handlers + \
	stfexp_constraint_parent.register_stf_handlers + \
	stfexp_constraint_ik.register_stf_handlers + \
	stfexp_lightprobe_anchor.register_stf_handlers + \
	stfexp_collider_sphere.register_stf_handlers + \
	stfexp_collider_capsule.register_stf_handlers + \
	stfexp_collider_plane.register_stf_handlers + \
	stfexp_camera.register_stf_handlers + \
	stfexp_light.register_stf_handlers + \
	stfexp_instance_text.register_stf_handlers + \
	stfexp_node_ethereal.register_stf_handlers
