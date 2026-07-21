
"""
Core STF resources for basic 3d model concepts.

Should be fully supported by every STF implementation.
"""

__all__ = ["register_stf_handlers"]


from .stf_prefab.stf_prefab import Handler_STF_Prefab
from .stf_node.stf_node import Handler_STF_Node
from .stf_instance_mesh.stf_instance_mesh import Handler_STF_Instance_Mesh
from .stf_mesh.stf_mesh import Handler_STF_Mesh
from .stf_material.stf_material import Handler_STF_Material
from .stf_instance_armature.stf_instance_armature import Handler_STF_Instance_Armature
from .stf_armature.stf_armature import Handler_STF_Armature
from .stf_bone.stf_bone import Handler_STF_Bone
from .stf_image.stf_image import Handler_STF_Image
from .stf_texture.stf_texture import Handler_STF_Texture
from .stf_animation.stf_animation import Handler_STF_Animation


register_stf_handlers = [
	Handler_STF_Prefab,
	Handler_STF_Node,
	Handler_STF_Instance_Mesh,
	Handler_STF_Mesh,
	Handler_STF_Material,
	Handler_STF_Instance_Armature,
	Handler_STF_Armature,
	Handler_STF_Bone,
	Handler_STF_Image,
	Handler_STF_Texture,
	Handler_STF_Animation,
]
