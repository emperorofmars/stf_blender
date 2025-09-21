
from . import org_blender_armature_display
from . import org_blender_instance_armature_display
from . import org_blender_object_rotation_mode

register_stf_modules = \
	org_blender_armature_display.register_stf_modules + \
	org_blender_instance_armature_display.register_stf_modules + \
	org_blender_object_rotation_mode.register_stf_modules
