
from enum import Enum


class STFReportSeverity(Enum):
	Debug = 0
	Info = 1
	Warn = 2
	Error = 3
	FatalError = 4


class STFReport:
	def __init__(self, message: str, severity: STFReportSeverity = STFReportSeverity.Error, stf_id: str = None, stf_type: str = None, application_object: any = None):
		self.message = message
		self.severity = severity
		self.stf_id = stf_id
		self.stf_type = stf_type
		self.application_object = application_object

	def to_string(self) -> str:
		self.severity.name
		ret = "== STF " + self.severity.name + " =="
		if(self.stf_type): ret += "\nSTF Type: " + str(self.stf_type)
		if(self.stf_id): ret += "\nID: " + str(self.stf_id)
		if(self.application_object is not None): ret += "\nApp Object: " + str(self.application_object)
		ret += "\nMessage:\n" + self.message
		return ret


class STFException(Exception):
	def __init__(self, stf_report: STFReport, *args):
		self.stf_report = stf_report
		super().__init__(*args)
