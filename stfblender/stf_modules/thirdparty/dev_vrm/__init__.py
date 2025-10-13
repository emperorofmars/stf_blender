
from . import dev_vrm_blendshape_pose
from .import dev_vrm_springbone

register_stf_modules = \
	dev_vrm_blendshape_pose.register_stf_modules + \
	dev_vrm_springbone.register_stf_modules
