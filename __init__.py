from . import auto_load
from .stfblender import package_key


package_key.package_key = __package__


auto_load.init()


def register():
	from .stfblender_common import register
	register()
	auto_load.register()

def unregister():
	from .stfblender_common import unregister
	auto_load.unregister()
	unregister()


# Expose STF handlers to be loaded by `stfblender_common.resource.stf_registry`
from .stfblender.stf_resources import register_stf_handlers

