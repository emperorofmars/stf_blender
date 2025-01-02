

from .stf_report import STF_Report_Severity, STFReport

def run_tasks(self):
	max_iterations = 1000
	while(len(self._tasks) > 0 and max_iterations > 0):
		taskset = self._tasks
		self._tasks = []
		for task in taskset:
			task()
		max_iterations -= 1
	if(len(self._tasks) > 0):
		self.report(STFReport(message="Recursion", severity=STF_Report_Severity.Error))
