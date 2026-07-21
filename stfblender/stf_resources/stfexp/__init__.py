
"""
Expanded STF resources that provide additional functionality.

May not be supported by every STF implementation fully.
"""

__all__ = ["register_stf_handlers"]


from .stfexp_mesh_seams import Handler_STF_Mesh_Seams, HOOK_STFEXP_Mesh_Seams
from .stfexp_mesh_creases import Handler_STF_Mesh_Creases, HOOK_STFEXP_Mesh_Creases
from .stfexp_armature_humanoid import Handler_STFEXP_Armature_Humanoid
from .stfexp_constraint_twist import Handler_STFEXP_Constraint_Twist
from .stfexp_constraint_rotation import Handler_STFEXP_Constraint_Rotation
from .stfexp_constraint_parent import Handler_STFEXP_Constraint_Parent
from .stfexp_constraint_ik import Handler_STFEXP_Constraint_IK
from . import stfexp_lightprobe_anchor
from . import stfexp_collider_sphere
from . import stfexp_collider_capsule
from . import stfexp_collider_plane
from . import stfexp_camera
from . import stfexp_light
from .stfexp_instance_text import Handler_STFEXP_Instance_Text
from .stfexp_text.stfexp_text import Handler_STFEXP_Text
from .stfexp_animation_blendtree import Handler_STFEXP_Animation_Blendtree
from .stfexp_node_ethereal import Handler_STFEXP_Node_Ethereal


register_stf_handlers = [
	Handler_STF_Mesh_Seams,
	HOOK_STFEXP_Mesh_Seams,
	Handler_STF_Mesh_Creases,
	HOOK_STFEXP_Mesh_Creases,
	Handler_STFEXP_Armature_Humanoid,
	Handler_STFEXP_Constraint_Twist,
	Handler_STFEXP_Constraint_Rotation,
	Handler_STFEXP_Constraint_Parent,
	Handler_STFEXP_Constraint_IK,

	Handler_STFEXP_Instance_Text,
	Handler_STFEXP_Text,
	Handler_STFEXP_Animation_Blendtree,
	Handler_STFEXP_Node_Ethereal,
] + \
	stfexp_lightprobe_anchor.register_stf_handlers + \
	stfexp_collider_sphere.register_stf_handlers + \
	stfexp_collider_capsule.register_stf_handlers + \
	stfexp_collider_plane.register_stf_handlers + \
	stfexp_camera.register_stf_handlers + \
	stfexp_light.register_stf_handlers
