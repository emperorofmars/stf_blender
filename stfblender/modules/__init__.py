
from . import core
from . import expanded
from . import ava
from . import thirdparty

register_stf_modules = core.register_stf_modules + ava.register_stf_modules + expanded.register_stf_modules + thirdparty.register_stf_modules
