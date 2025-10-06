
from . import core
from . import expanded
from . import ava
from . import thirdparty
from . import placeholder_for_testing
from . import fallback

register_stf_modules = core.register_stf_modules + expanded.register_stf_modules + ava.register_stf_modules + thirdparty.register_stf_modules + placeholder_for_testing.register_stf_modules + fallback.register_stf_modules
