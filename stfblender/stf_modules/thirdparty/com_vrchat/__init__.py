
from . import vrc_avatar_colliders
from . import vrc_physbone
from . import vrc_contact_sender
from . import vrc_contact_receiver

register_stf_modules = \
	vrc_avatar_colliders.register_stf_modules + \
	vrc_physbone.register_stf_modules + \
	vrc_contact_sender.register_stf_modules + \
	vrc_contact_receiver.register_stf_modules
