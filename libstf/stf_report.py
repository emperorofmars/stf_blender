
from enum import Enum


class STF_Report_Severity(Enum):
	Debug = 0
	Info = 1
	Warn = 2
	Error = 3


class STFReport:
	stf_severity: STF_Report_Severity
	stf_id: str
	stf_type: str
	application_object: any
	message: str


class STFException(Exception):
	stf_report: STFReport
