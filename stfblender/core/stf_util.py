from typing import Callable
from .stf_report import STFReportSeverity, STFException, STFReport


class StateUtil:
	def __init__(self, fail_on_severity = STFReportSeverity.FatalError):
		self._tasks: list[Callable] = []
		self._cleanup_tasks: list[Callable] = []
		self._reports: list[STFReport] = []
		self._fail_on_severity = fail_on_severity

	def report(self, report: STFReport):
		self._reports.append(report)
		if(report.severity.value >= self._fail_on_severity.value):
			print(report.to_string() + "\n", flush=True)
			raise STFException(report)

	def add_task(self, task: Callable):
		self._tasks.append(task)

	def add_cleanup_task(self, task: Callable):
		self._cleanup_tasks.append(task)

	def run_tasks(self):
		max_iterations = 1000
		while(len(self._tasks) > 0 and max_iterations > 0):
			taskset = self._tasks
			self._tasks = []
			for task in taskset:
				task()
			max_iterations -= 1
		if(len(self._tasks) > 0):
			self.report(STFReport(message="Task Recursion", severity=STFReportSeverity.FatalError))

		max_iterations = 1000
		while(len(self._cleanup_tasks) > 0 and max_iterations > 0):
			taskset = self._cleanup_tasks
			self._cleanup_tasks = []
			for task in taskset:
				task()
			max_iterations -= 1
		if(len(self._cleanup_tasks) > 0):
			self.report(STFReport(message="Task Recursion", severity=STFReportSeverity.FatalError))
