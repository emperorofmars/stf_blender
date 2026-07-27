
from .dev_vrm_springbone  import Handler_VRM_Springbone
from .dev_vrm_blendshape_pose import Handler_VRM_Blendshape_Pose

__all__ = ["register_stf_handlers"]

register_stf_handlers = [Handler_VRM_Springbone, Handler_VRM_Blendshape_Pose]
