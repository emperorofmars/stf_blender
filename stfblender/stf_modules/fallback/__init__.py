from .json_fallback_component import register_stf_modules as fallback_component
from .json_fallback_data import register_stf_modules as fallback_data


register_stf_modules = fallback_component + fallback_data
