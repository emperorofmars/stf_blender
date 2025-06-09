import bpy


def set_instance_blendshapes(blender_object: bpy.types.Object):
	blender_mesh = blender_object.data
	if(blender_mesh.shape_keys):
		for blendshape in blender_mesh.shape_keys.key_blocks:
			for instance_blendshape in blender_object.stf_instance_mesh.blendshape_values:
				if(instance_blendshape.name == blendshape.name):
					break
			else:
				instance_blendshape = blender_object.stf_instance_mesh.blendshape_values.add()
				instance_blendshape.name = blendshape.name
				instance_blendshape.value = blendshape.value

