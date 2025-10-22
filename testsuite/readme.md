# STF Blender Test Suite
Requires a local Blender installation with the STF extension enabled.

## Run Tests
Run in the repo's root directory!\
*Change the Blender version in the path accordingly.*

### Raw
Won't modify Blender's Python environment.
* Windows
	* Git Bash
		```sh
		"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b --factory-startup -P testsuite/run_testsuite.py
		```

### With Coverage
Install `coverage` to Blenders Python environment.
* Windows
	* Git Bash
		* Install
			```sh
			"C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe" -m ensurepip
			"C:\Program Files\Blender Foundation\Blender 4.5\4.5\python\bin\python.exe" -m pip install coverage
			```
		* Run
			```sh
			"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b --factory-startup --python-use-system-env -P testsuite/run_testsuite.py
			```

