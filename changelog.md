# Changelog

## v0.1.11
* Code cleanup & improved type annotations in common.
* Uses multiline textboxes & labels if possible.
* Serializes blenders "Empty" display settings.
* `stfexp.instance.text` bugfix.

## v0.1.10
* Poll function bugfixes when checking whether a bone is selected.

## v0.1.9
* `stf.animation` handles SlotLink target-collection.
* `stf.instance.mesh`: simplified instance shape key overrides GUI and data-model.
	* This is backwards compatible.
	* If you set-up overrides previously, you'll find that all shape keys to have an override. Feel free to press the `Remove Unmodified Shape Key Overrides` button for some cleanup^^
* Added primitive GUI to Collections to show which animations can be exported, if SlotLink v0.2 or higher is used.
* Added the ability for handlers to programmatically determine their priority.
* Improved the handling of resources that imported into a fallback representation.

## v0.1.8
* Adapted `stf.animation` to support SlotLink v0.2.x with multiple targets per slot.
	* Previous SlotLink versions are not supported. SlotLink animations with the old data-model have to be migrated with one convenient button-press.
* Improved logging & error messages.
* Prevent faulty import of component-resources, i.e. when a fallback resource referenced a component from another resource, that didn't import correctly.
* `ava.expressions` can handle animations that were not exported.
* `stfexp.armature.humanoid` fixed operator button parameters.

## v0.1.7
* The codebase received a biiiig refactoring
	* Everything needed to create separate STF resource extension for Blender has been moved to the stfblender_common Git submodule.\
		It can be safely included by multiple Blender extensions!\
		See the custom STF extension template for an example.
	* Handlers now mostly define abstract classmethods for nearly everything, leading to much better tooling/autocomplete support. It is also more consistent with Blenders own API.
	* One time renaming of most of these interface methods, to be consistent and make far more sense.
	* Vastly improved docstrings.
	* GUI drawing for Blender native resources also uses the stf_registry to determine the Handler for doing so.
* The usual bugfixes.

## v0.1.6
* fixed export filename bug https://codeberg.org/stf_format/stf_blender/issues/1
* improved code quality / added docstrings to lots of central code

## v0.1.5
* minor binary format adaptation
* simplified export ux
