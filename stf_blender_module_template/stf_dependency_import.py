import bpy
import addon_utils


__installed_and_enabled_stf_extensions = []
for m in {m.module for m in bpy.context.preferences.extensions.repos}:
	loaded_default, loaded_state = addon_utils.check("bl_ext." + m + ".stf_blender")
	if(loaded_state or m == "vscode_development"):
		__installed_and_enabled_stf_extensions.append(m)

if("vscode_development" in __installed_and_enabled_stf_extensions):
	print("Enabling Custom STF Modules for development extension.")
	selected_stf_extension = "bl_ext.vscode_development.stf_blender"
elif(len(__installed_and_enabled_stf_extensions) == 1):
	print("Enabling Custom STF Modules!")
	selected_stf_extension = "bl_ext." + __installed_and_enabled_stf_extensions[0] + ".stf_blender"
elif(len(__installed_and_enabled_stf_extensions) > 1):
	print("Warning: STF Module detected more than one enabled STF extension! Using the first one from the '" + __installed_and_enabled_stf_extensions[0] + "' repository")
	selected_stf_extension = "bl_ext." + __installed_and_enabled_stf_extensions[0] + ".stf_blender"
else:
	print("No STF Extension detected. Not enabling Custom STF Modules!")



if(selected_stf_extension):
	import importlib
	libstf = importlib.import_module(selected_stf_extension + ".libstf")
	stfblender = importlib.import_module(selected_stf_extension + ".stfblender")

