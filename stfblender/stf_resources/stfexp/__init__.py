
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
from .stfexp_lightprobe_anchor import Handler_STFEXP_LightprobeAnchor
from .stfexp_collider_sphere import Handler_STFEXP_Collider_Sphere
from .stfexp_collider_capsule import Handler_STFEXP_Collider_Capsule
from .stfexp_collider_plane import Handler_STFEXP_Collider_Plane
from .stfexp_camera import Handler_STFEXP_Camera
from .stfexp_light import Handler_STFEXP_Light
from .stfexp_instance_text import Handler_STFEXP_Instance_Text
from .stfexp_text import Handler_STFEXP_Text
from .stfexp_curve import Handler_STFEXP_Curve
from .stfexp_instance_curve import Handler_STFEXP_Instance_Curve
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
	Handler_STFEXP_LightprobeAnchor,
	Handler_STFEXP_Collider_Sphere,
	Handler_STFEXP_Collider_Capsule,
	Handler_STFEXP_Collider_Plane,
	Handler_STFEXP_Camera,
	Handler_STFEXP_Light,
	Handler_STFEXP_Instance_Text,
	Handler_STFEXP_Text,
	Handler_STFEXP_Instance_Curve,
	Handler_STFEXP_Curve,
	Handler_STFEXP_Animation_Blendtree,
	Handler_STFEXP_Node_Ethereal,
]
