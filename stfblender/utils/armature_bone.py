import bpy

class ArmatureBone:
	def __init__(self, armature: bpy.types.Armature, bone: str):
		self.armature = armature
		self.bone = bone

	def get_bone(self) -> bpy.types.Bone:
		return self.armature.bones[self.bone]

	def get_edit_bone(self) -> bpy.types.Bone:
		return self.armature.edit_bones[self.bone]

	def get_name(self) -> str:
		return self.bone
