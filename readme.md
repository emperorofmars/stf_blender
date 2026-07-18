# STF Blender
**Squirrel Transfer Format - Modular 3D File-Format**\
*Intended for (not only) games-development use-cases.*

**WIP implementation for Blender 4.5+. Do not use productively!**

🌰 **[Read the User Guide!](https://docs.stfform.at/guide/blender.html)** 🌰 **[Report Issues](https://codeberg.org/stf_format/stf_blender/issues)** 🌰 **[STF Documentation](https://docs.stfform.at/)**

## Installation
### From Repository (preferred)
Follow the steps on [docs.stfform.at](https://docs.stfform.at/installation/blender.html)!

### Manual
Download the [latest release](https://codeberg.org/stf_format/stf_blender/releases/latest)\
Add it under: `Edit` → `Preferences` → `Get Extensions` → **Click on the top right most dropdown** → `Install from Disk...`

---

> [!TIP]
> **Also install the [Slot Link](https://extensions.blender.org/add-ons/slot-link/) extension if you want to import/export animations.**

Please open issues for any bugs or misbehavior you notice. Feel free to open issues for feature requests.

## Development Setup
* After cloning, change into the repo dir and run:
	``` sh
	git submodule update --init
	```
* Have an up to date version of Blender installed.
* Either:
	* Use `bpydev.py` included in this repository.
	* Use VSCode with the [recommended extensions](./.vscode/extensions.json).\
		The most important one is [Blender VS Code](https://github.com/JacquesLucke/blender_vscode).
* Create a Python 3.13 venv in the repo directory.
* Inside the venv run:
	``` sh
	pip install -r requirements.txt
	```

## Contributing
Human made contributions via pull-requests are very welcome.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## License
All source-code in this repository, except when noted in individual files and/or directories, is licensed under either:

* MIT License (LICENSE-MIT or <https://opensource.org/license/MIT>)
* Apache License, Version 2.0 (LICENSE-APACHE2 or http://www.apache.org/licenses/LICENSE-2.0)

<!--
**Build the extension**

Install dependencies (preferably into a venv):
``` sh
pip install -r requirements.txt
```

Build the extension:
``` python
python bpydev.py package -o packages
```
-->
