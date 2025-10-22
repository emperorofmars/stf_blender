# STF Blender
**Squirrel Transfer Format - Modular 3D File-Format**\
*Intended for (not only) games-development use-cases.*

**WIP implementation for Blender 4.5+. Do not use productively!**

**[Read the User Guide!](https://docs.stfform.at/guide/blender.html)** ⭐ **[STF Website](https://docs.stfform.at/)**

## Installation
### From Repository (preferred)
Follow the steps on [docs.stfform.at](https://docs.stfform.at/installation/blender.html)!

### Manual
Download the [latest release](https://github.com/emperorofmars/stf_blender/releases/latest)\
Add it under: `Edit` -> `Preferences` -> `Get Extensions` -> **Click on the top right most dropdown** -> `Install from Disk...`

---

**Also install the [Slot Link](https://extensions.blender.org/add-ons/slot-link/) extension if you want to import/export animations.**

## License
All source-code in this repository, except when noted in individual files and/or directories, is licensed under either:

* MIT License (LICENSE-MIT or <https://opensource.org/license/MIT>)
* Apache License, Version 2.0 (LICENSE-APACHE2 or http://www.apache.org/licenses/LICENSE-2.0)

<!--
**Commands to build the extension.**\
*Change the Blender version in the path accordingly.*

* Windows Git Bash
	* Build Extension
		```sh
		"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --command extension build --output-dir=./packages
		```
	* Generate Repository Json
		```sh
		"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" --command extension server-generate --repo-dir=./packages
		```
-->
