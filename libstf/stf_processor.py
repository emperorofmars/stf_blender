from typing import Callable

from .stf_export_context import STF_ExportContext
from .stf_import_context import STF_ImportContext


class STF_Processor:
	type: str
	kind: str
	import_func: Callable[[STF_ImportContext, dict], any]
	export_func: Callable[[STF_ExportContext, any], dict]
