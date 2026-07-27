
from .vrc_avatar_colliders import Handler_VRC_AvatarColliders
from . import vrc_physbone
from . import vrc_contact_sender
from . import vrc_contact_receiver

__all__ = ["register_stf_handlers"]

register_stf_handlers = [
	Handler_VRC_AvatarColliders
] + \
	vrc_physbone.register_stf_handlers + \
	vrc_contact_sender.register_stf_handlers + \
	vrc_contact_receiver.register_stf_handlers
