# OpenFront Auto-Placer

A Windows utility that automates OpenFront building shortcuts and mouse clicks. It includes a graphical interface and a console mode.

The tool sends input only while `OpenFront.exe` is the foreground window, using the current mouse position. It does not select a map location for you.

## Requirements

- Windows 10 or 11
- Python 3.11 or later to run from source
- OpenFront for Windows

## Run from source

From the project directory, create an environment, install the requirements, and start the GUI:

```bat
py -3.11 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m src.gui_main
```

The first run creates `config.toml` from `config.toml.default`. The GUI lets you configure hotkeys and timing, apply or save settings, and launch the game. The console version is also available:

```bat
.venv\Scripts\python.exe -m src.main
```

## Use

Focus the game and point to a valid location on the map. Use the configured hotkey or select a building in the GUI to start placing it; activate it again to stop. **Pause/Break** also stops placement. The tool pauses automatically when the game loses focus.

Placement is performed at the cursor, so keep it over the intended map location. The default session limit is 5,000 placements; set `max_iterations_per_session` to `0` for no limit.

The game's ×5 setting applies to eligible upgrades and atomic bomb salvos, not to placing five new buildings. Check for the in-game ×5 indicator before relying on it.

## Build

On Windows, run `make.bat`. It creates `dist\OpenFrontAutoPlacer.exe`, which includes the required runtime and assets. Run the executable from a writable folder so it can create `config.toml` beside itself.

## Test

Run the test suite from the project directory:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests
```

The tests mock system input. Verify game interaction and executable builds on Windows.

## Disclaimer

This is an unofficial community tool. Use it only where automation is permitted by the game's rules. Use at your own risk.
