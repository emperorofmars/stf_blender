import bpy

from .package_key import package_key
from .utils.minsc import draw_slot_link_warning

class STF_Extension_Preferences(bpy.types.AddonPreferences):
	bl_idname = package_key

	#enable_dev_mode: bpy.props.BoolProperty(name="Enable Development Mode", default=False) # type: ignore

	def draw(self, context):
		self.layout.label(text="Thanks for using STF!")
		draw_slot_link_warning(self.layout)


