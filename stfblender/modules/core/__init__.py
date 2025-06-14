
from .stf_prefab import stf_prefab
from .stf_node import stf_node
from .stf_instance_mesh import stf_instance_mesh
from .stf_mesh import stf_mesh
from .stf_material import stf_material
from .stf_armature import stf_armature
from .stf_instance_armature import stf_instance_armature
from .stf_bone import stf_bone
from .stf_image import stf_image
from .stf_texture import stf_texture
from .stf_animation import stf_animation

register_stf_modules = \
	stf_prefab.register_stf_modules \
	+ stf_node.register_stf_modules \
	+ stf_instance_mesh.register_stf_modules \
	+ stf_mesh.register_stf_modules \
	+ stf_material.register_stf_modules \
	+ stf_armature.register_stf_modules \
	+ stf_instance_armature.register_stf_modules \
	+ stf_bone.register_stf_modules \
	+ stf_image.register_stf_modules \
	+ stf_texture.register_stf_modules \
	+ stf_animation.register_stf_modules \
