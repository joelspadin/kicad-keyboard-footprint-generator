# KiCad Keyboard Footprint Generator

This repository contains scripts to generate KiCad footprints for mechanical keyboard components such as Cherry MX switches.

MX footprints are based on the [Official KiCad Library](https://gitlab.com/kicad/libraries/kicad-footprints/-/tree/master/Button_Switch_Keyboard.pretty) and [ai03's MX/Alps Library](https://github.com/ai03-2725/MX_Alps_Hybrid).

The [hotswap socket 3D model](https://grabcad.com/library/kailh-pg1511-hotswap-socket-1) is made by Evgeny Klypa and adjusted to be centered on the footprint.

## Usage

These scripts require [Python 3.10 or newer](https://www.python.org/downloads/). Run the following command to install dependencies:

```sh
pip3 install .
```

Run one of the scripts from the `scripts` directory to generate a library. The footprints can be customized and extra variations can be generated with command line arguments. Use the `--help` argument to see a list of supported options.

By default the scripts will create a library at `./out/{name}.pretty`, where `{name}` matches the script name (e.g. `make_mx_hotswap.py` will create `MX_Hotswap.pretty`). The `--out` argument changes the output directory, and the `--name` argument changes the library name.

The scripts generate footprints for standard key sizes up to 7U. To make additional sizes, edit the size arrays in [scripts/tools/mx.py](scripts/tools/mx.py) or create your own scripts that use the `KicadKeyboardFootprints` module.

### Examples

```sh
# Add hotswap MX switch footprints
./scripts/make_mx_hotswap.py

# Add hotswap MX switch footprints with anti-shear pads
./scripts/make_mx_hotswap.py --pads antishear

# Add solder MX switch footprints to ~/projects/widget/keyboard.pretty
./scripts/make_mx_hotswap.py --out ~/projects/widget --name keyboard
```

## Development

Run the following commands to install all dependencies for the project and enable code checkers:

```sh
pip3 install .[dev]
pre-commit install
```

[pre-commit](https://pre-commit.com/) will now automatically check your code when you make a commit.

You can manually run the checks by running:

```sh
pre-commit run
```

Or to check the entire project instead of just your changes:

```sh
pre-commit run --all-files
```

### Visual Studio Code

If you install the recommended extensions, workspace settings will be initialized from [.vscode/settings.default.json](.vscode/settings.default.json). This enables automatic code formatting and linting. You can further customize your settings as you like.
