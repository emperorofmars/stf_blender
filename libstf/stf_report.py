
from enum import Enum


class STF_Report_Severity(Enum):
	Debug = 0
	Info = 1
	Warn = 2
	Error = 3


class STFReport:
	severity: STF_Report_Severity
	stf_id: str
	stf_type: str
	application_object: any
	message: str

	def __init__(self, message: str, severity: STF_Report_Severity = STF_Report_Severity.Error, stf_id: str = None, stf_type: str = None, application_object: any = None):
		self.message = message
		self.severity = severity
		self.stf_id = stf_id
		self.stf_type = stf_type
		self.application_object = application_object


class STFException(Exception):
	stf_report: STFReport

	def __init__(self, stf_report: STFReport, *args):
		self.stf_report = stf_report
		super().__init__(*args)
