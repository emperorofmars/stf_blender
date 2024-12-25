from typing import Callable


class STF_Processor:
	stf_type: str
	stf_kind: str
	understood_types: list = []
	import_func: Callable[[any, dict, str], any]
	export_func: Callable[[any, any], tuple[dict, str]]


# from .stf_export_context import STF_ExportContext
# from .stf_import_context import STF_ImportContext
