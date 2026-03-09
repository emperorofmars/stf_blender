import bpy


def instance_blendshapes_requires_update(blender_object: bpy.types.Object) -> bool:
	blender_mesh: bpy.types.Mesh = blender_object.data
	if(blender_mesh.shape_keys and len(blender_mesh.shape_keys.key_blocks) > 0):
		if(len(blender_mesh.shape_keys.key_blocks) != len(blender_object.stf_instance_mesh.blendshape_values)):
			return True

		for blendshape in blender_mesh.shape_keys.key_blocks:
			if(blendshape.name not in blender_object.stf_instance_mesh.blendshape_values):
				return True

		for instance_blendshape in blender_object.stf_instance_mesh.blendshape_values:
			if(instance_blendshape.name not in blender_mesh.shape_keys.key_blocks):
				return True

	return False


def set_instance_blendshapes(blender_object: bpy.types.Object):
	blender_mesh: bpy.types.Mesh = blender_object.data
	if(blender_mesh.shape_keys and len(blender_mesh.shape_keys.key_blocks) > 0):
		for blendshape in blender_mesh.shape_keys.key_blocks:
			if(blendshape.name in blender_object.stf_instance_mesh.blendshape_values):
				instance_blendshape = blender_object.stf_instance_mesh.blendshape_values[blendshape.name]
				if(not instance_blendshape.override):
					instance_blendshape.value = blendshape.value # update values of non overridden blendshapes to those of the base mesh
			else:
				instance_blendshape = blender_object.stf_instance_mesh.blendshape_values.add()
				instance_blendshape.name = blendshape.name
				instance_blendshape.value = blendshape.value

		instance_index = 0
		for _ in range(len(blender_object.stf_instance_mesh.blendshape_values)):
			if(blender_object.stf_instance_mesh.blendshape_values[instance_index].name in blender_mesh.shape_keys.key_blocks):
				instance_index += 1
			else:
				blender_object.stf_instance_mesh.blendshape_values.remove(instance_index)

		for index, blendshape in enumerate(blender_mesh.shape_keys.key_blocks):
			blender_object.stf_instance_mesh.blendshape_values[blendshape.name].index_on_mesh = index

	else:
		blender_object.stf_instance_mesh.blendshape_values.clear()
