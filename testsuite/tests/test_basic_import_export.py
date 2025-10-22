import bpy
import unittest


class TestBasicImportExport(unittest.TestCase):

	def test_import(self):
		try:
			ret = bpy.ops.stf.import_files("EXEC_DEFAULT", directory="testsuite/assets", files=[{"name":"default_cube.stf"}])
			self.assertTrue("FINISHED" in ret)
		except Exception as e:
			self.fail(str(e))

	def test_export(self):
		try:
			ret = bpy.ops.stf.export("EXEC_DEFAULT", filepath="testsuite/output/ret.stf", debug=True)
			self.assertTrue("FINISHED" in ret)
		except Exception as e:
			self.fail(str(e))

