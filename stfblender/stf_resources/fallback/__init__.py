
"""
Special STF resource handlers for resources that don't have a handler registered.
"""

from .json_fallback_component import Handler_JsonFallbackComponent
from .json_fallback_instance import Handler_JsonFallbackInstance
from .json_fallback_nonnative import Handler_JsonFallbackNonNative

__all__ = ["register_stf_handlers"]

register_stf_handlers = [Handler_JsonFallbackComponent, Handler_JsonFallbackInstance, Handler_JsonFallbackNonNative]
