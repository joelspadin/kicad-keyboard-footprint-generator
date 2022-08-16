# KiCad Keyboard Footprint Generator

This repository contains scripts to generate KiCad footprints for mechanical keyboard components such as Cherry MX switches.

MX footprints are based on the [Official KiCad Library](https://gitlab.com/kicad/libraries/kicad-footprints/-/tree/master/Button_Switch_Keyboard.pretty) and [ai03's MX/Alps Library](https://github.com/ai03-2725/MX_Alps_Hybrid).



## Usage

Run one of the scripts from the `scripts` directory to generate a library. The footprints can be customized and extra variations can be generated with command line arguments. Use the `--help` argument to see a list of supported options.

By default the scripts will create a library at `./out/{name}.pretty`, where `{name}` matches the script name, e.g. `make_mx_hotswap.py` will create `MX_Hotswap.pretty`. The `--out` argument changes the output directory, and the `--name` argument changes the library name.

Due to a limitation in KiCad, any 3D models associated with footprints have their file paths relative to the project directory. If you want to place libraries in a subdirectory, include the subdirectory name in the `--name` argument, e.g. `--name libraries/MX_Hotswap` will set the paths correctly if the library is located at `libraries/MX_Hotswap.pretty` inside your project.

The scripts generate footprints for standard key sizes up to 7U. To make additional sizes, edit the size arrays in [scripts/tools/mx.py](scripts/tools/mx.py) or create your own scripts that use the `KicadKeyboardFootprints` module.

### Examples

```bash
# Add hotswap MX switch footprints
./scripts/make_mx_hotswap.py

# Add hotswap MX switch footprints with anti-shear pads
./scripts/make_mx_hotswap.py --pads antishear

# Add solder MX switch footprints to ~/projects/widget/keyboard.pretty
./scripts/make_mx_hotswap.py --out ~/projects/widget --name keyboard
```

