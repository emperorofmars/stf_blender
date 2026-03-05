from .json_fallback_component import register_stf_handlers as fallback_component
from .json_fallback_data import register_stf_handlers as fallback_data


register_stf_handlers = fallback_component + fallback_data
