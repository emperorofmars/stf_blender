
from .stf_prefab import stf_prefab
from .stf_node_spatial import stf_node_spatial

register_stf_modules = \
	stf_prefab.register_stf_modules \
	+ stf_node_spatial.register_stf_modules \

