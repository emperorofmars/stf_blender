# STF Blender Test Suite
Requires a local Blender installation with the STF extension enabled.

## Run Tests
Run in the repo's root directory!\
*Change the Blender version and path accordingly.*

* Set Blender Path Variable
	* Windows (Git Bash)
		``` sh
		BLENDER_PATH="C:\Program Files\Blender Foundation\Blender 4.5\blender.exe"
		```
	* Linux Bash
		``` sh
		BLENDER_PATH=~/Software/blender/blender-5.0.1-linux-x64/blender
		```

### Raw
Won't modify Blender's Python environment.
```sh
$BLENDER_PATH -b --factory-startup -P testsuite/run_testsuite.py
```

### With Coverage
Install `coverage` to Blenders Python environment.
* Install
	```sh
	$BLENDER_PATH -m ensurepip
	$BLENDER_PATH -m pip install coverage
	```
* Run
	```sh
	$BLENDER_PATH -b --factory-startup --python-use-system-env -P testsuite/run_testsuite.py
	```

