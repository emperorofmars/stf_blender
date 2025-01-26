from . import auto_load

auto_load.init()

def register():
	auto_load.register()

def unregister():
	auto_load.unregister()


from .stfblender import modules_core
from .stfblender import modules_expanded
from .stfblender import modules_ava

register_stf_modules = modules_core.register_stf_modules + modules_expanded.register_stf_modules + modules_ava.register_stf_modules
