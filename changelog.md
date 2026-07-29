# Changelog

## v0.1.8
* Adapted `stf.animation` to support SlotLink v0.2.x with multiple targets per slot.
* Improved logging & error messages.
* Prevent faulty import of component-resources, i.e. when a fallback resource referenced a component from another resource, that didn't import correctly.
* `ava.expressions` can handle animations that were not exported.

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
