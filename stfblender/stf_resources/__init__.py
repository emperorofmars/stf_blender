
"""
Handlers for import & export of STF resources.
"""

from . import stf
from . import stfexp
from . import ava
from . import thirdparty
from . import placeholder_for_testing
from . import fallback

register_stf_handlers = stf.register_stf_handlers + stfexp.register_stf_handlers + ava.register_stf_handlers + thirdparty.register_stf_handlers + placeholder_for_testing.register_stf_handlers + fallback.register_stf_handlers
