import bpy

# import
ret = bpy.ops.stf.import_files("EXEC_DEFAULT", directory="assets", files=[{"name":"default_cube.stf"}])
for r in ret:
	assert(r == "FINISHED")
	break

# export
ret = bpy.ops.stf.export("EXEC_DEFAULT", filepath="output/ret.stf", debug=True)
for r in ret:
	assert(r == "FINISHED")
	break

