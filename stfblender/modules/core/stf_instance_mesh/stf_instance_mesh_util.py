import bpy


def set_instance_blendshapes(blender_object: bpy.types.Object):
	blender_mesh: bpy.types.Mesh = blender_object.data
	if(blender_mesh.shape_keys):
		for blendshape in blender_mesh.shape_keys.key_blocks:
			for instance_blendshape in blender_object.stf_instance_mesh.blendshape_values:
				if(instance_blendshape.name == blendshape.name):
					if(not instance_blendshape.override):
						instance_blendshape.value = blendshape.value # update values of non overridden blendshapes to those of the base mesh
					break
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
	else:
		blender_object.stf_instance_mesh.blendshape_values.clear()



def set_instance_materials(blender_object: bpy.types.Object):
	blender_mesh: bpy.types.Mesh = blender_object.data
	while(len(blender_object.stf_instance_mesh.materials) < len(blender_mesh.materials)):
		blender_object.stf_instance_mesh.materials.add()

	while(len(blender_object.stf_instance_mesh.materials) > len(blender_mesh.materials)):
		blender_object.stf_instance_mesh.materials.remove(len(blender_object.stf_instance_mesh.materials) - 1)

	for material_index in range(len(blender_mesh.materials)):
		if(not blender_object.stf_instance_mesh.materials[material_index].override):
			blender_object.stf_instance_mesh.materials[material_index].material = blender_mesh.materials[material_index]

