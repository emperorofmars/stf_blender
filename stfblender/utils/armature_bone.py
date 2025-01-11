import bpy

class ArmatureBone:
	def __init__(self, armature: bpy.types.Armature, bone_name: str):
		self.armature = armature
		self.name = bone_name
		self.stf_id = self.armature.bones[bone_name].stf_id

	def get_bone(self) -> bpy.types.Bone:
		return self.armature.bones[self.name]

	def get_edit_bone(self) -> bpy.types.Bone:
		return self.armature.edit_bones[self.name]
