
from .vrc_avatar_colliders import Handler_VRC_AvatarColliders
from .vrc_physbone import Handler_VRC_Physbone
from .vrc_contact_sender import Handler_VRC_ContactSender
from .vrc_contact_receiver import STF_Module_VRC_ContactReceiver

__all__ = ["register_stf_handlers"]

register_stf_handlers = [
	Handler_VRC_AvatarColliders,
	Handler_VRC_Physbone,
	Handler_VRC_ContactSender,
	STF_Module_VRC_ContactReceiver,
]
