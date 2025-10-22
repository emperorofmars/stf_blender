"""
$BLENDER_EXECUTABLE -b --factory-startup -P testsuite/run_testsuite.py

See readme.md for more info.
"""

STF_BLENDER_MODULE = "bl_ext.blender_stfform_at.stf_blender"


def setup_stf_extension():
	import bpy
	from pathlib import Path

	bpy.ops.wm.read_factory_settings(use_factory_startup_app_template_only=True)

	bpy.context.preferences.extensions.repos.new(
		name = "STF Testsuite Repository",
		module = "blender_stfform_at",
		custom_directory = str(Path(__file__).parent.parent.parent),
		source = "USER"
	)
	bpy.ops.preferences.addon_enable(module = STF_BLENDER_MODULE)

def cleanup_stf_extension():
	import bpy
	bpy.ops.preferences.addon_disable(module = STF_BLENDER_MODULE)


if __name__ == "__main__":
	import unittest
	from pathlib import Path

	loader = unittest.TestLoader()
	suite = loader.discover(str(Path(__file__).parent.joinpath("tests")))
	runner = unittest.TextTestRunner()

	use_coverage = False
	try:
		import coverage
		use_coverage = True
		print("Running STF testsuite with coverage")
	except:
		print("Running STF testsuite without coverage")

	setup_stf_extension()

	if(use_coverage):
		cov = coverage.Coverage(
			data_file=Path(__file__).parent.joinpath("report/.coverage"),
			omit=[
				"*/scripts/modules/addon_utils.py",
				"*/scripts/modules/bpy_types.py",
				"*/scripts/modules/bpy/*",
				"testsuite/tests/*"
			],
		)
		cov.start()

	runner.run(suite)

	if(use_coverage):
		cov.stop()

	cleanup_stf_extension()

	if(use_coverage):
		cov.save()
		cov.html_report(directory="testsuite/report")

	import bpy
	bpy.ops.wm.quit_blender()

