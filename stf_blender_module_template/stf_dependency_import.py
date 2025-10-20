import bpy
import addon_utils


__installed_and_enabled_stf_extensions = []
for m in {m.module for m in bpy.context.preferences.extensions.repos}:
	loaded_default, loaded_state = addon_utils.check("bl_ext." + m + ".stf_blender")
	if(loaded_state and m == "vscode_development"):
		__installed_and_enabled_stf_extensions.append(m)
	elif(loaded_state and m == "user_default"):
		__installed_and_enabled_stf_extensions.append(m)
	elif(loaded_state and m == "blender_stfform_at"):
		__installed_and_enabled_stf_extensions.append(m)
	elif(loaded_state and m == "blender_org"):
		__installed_and_enabled_stf_extensions.append(m)

if(len(__installed_and_enabled_stf_extensions) == 1):
	if("vscode_development" in __installed_and_enabled_stf_extensions):
		print("Enabling custom STF modules for development extension.")
		selected_stf_extension = "bl_ext.vscode_development.stf_blender"
	elif("blender_stfform_at" in __installed_and_enabled_stf_extensions):
		print("Enabling custom STF modules for official STF distribution.")
		selected_stf_extension = "bl_ext.blender_stfform_at.stf_blender"
	else:
		print("Enabling STF modules for user STF install!")
		selected_stf_extension = "bl_ext." + __installed_and_enabled_stf_extensions[0] + ".stf_blender"
elif(len(__installed_and_enabled_stf_extensions) > 1):
	print("Warning: Detected more than one enabled STF extension! Using the first one from the '" + __installed_and_enabled_stf_extensions[0] + "' repository")
	selected_stf_extension = "bl_ext." + __installed_and_enabled_stf_extensions[0] + ".stf_blender"
else:
	selected_stf_extension = None
	print("No STF extension detected. Not enabling custom STF modules!")

if(selected_stf_extension):
	import importlib
	stfblender = importlib.import_module(selected_stf_extension + ".stfblender")

