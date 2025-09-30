from . import auto_load
from .stfblender import package_key


package_key.package_key = __package__


auto_load.init()


def register():
	auto_load.register()

def unregister():
	auto_load.unregister()


# Expose all registered STF modules to be loaded
from .stfblender.stf_modules import register_stf_modules

