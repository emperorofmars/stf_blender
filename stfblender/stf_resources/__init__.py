
from . import core
from . import expanded
from . import ava
from . import thirdparty
from . import placeholder_for_testing
from . import fallback

register_stf_handlers = core.register_stf_handlers + expanded.register_stf_handlers + ava.register_stf_handlers + thirdparty.register_stf_handlers + placeholder_for_testing.register_stf_handlers + fallback.register_stf_handlers
