from . import auto_load

auto_load.init()


def register():
	auto_load.register()


def unregister():
	auto_load.unregister()


from .stfblender import register_stf_modules
