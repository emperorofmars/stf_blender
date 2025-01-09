
from .stf_prefab import stf_prefab
from .stf_node_spatial import stf_node_spatial
from .stf_instance_mesh import stf_instance_mesh
from .stf_mesh import stf_mesh
from .stf_material import stf_material
from .stf_instance_prefab import stf_instance_prefab

register_stf_modules = \
	stf_prefab.register_stf_modules \
	+ stf_node_spatial.register_stf_modules \
	+ stf_instance_mesh.register_stf_modules \
	+ stf_mesh.register_stf_modules \
	+ stf_material.register_stf_modules \
	+ stf_instance_prefab.register_stf_modules \
