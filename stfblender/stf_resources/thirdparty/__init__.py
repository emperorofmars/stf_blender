
from . import com_vrchat, org_blender, dev_vrm, com_squirrelbite

register_stf_handlers = com_vrchat.register_stf_handlers + org_blender.register_stf_handlers + dev_vrm.register_stf_handlers + com_squirrelbite.register_stf_handlers
