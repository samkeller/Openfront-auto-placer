# OpenFront Auto-Placer

A Windows tool for automating OpenFront building hotkeys and mouse clicks. It has a graphical interface and a console mode.

The tool sends input only while `OpenFront.exe` is the foreground window, at the current cursor position. It does not choose a map location for you.

## Requirements

- Windows 10 or later
- Python 3.11 or later to run from source
- OpenFront for Windows

## Install and run

Clone the repository, then run these commands from its folder:

```bat
git clone https://github.com/samkeller/Openfront-auto-placer.git
cd Openfront-auto-placer
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -e .
.venv\Scripts\python.exe -m src.gui_main
```

The first launch creates `config.toml` from `config.toml.default`. Configure hotkeys and timing in the GUI, then apply or save your settings. The console mode is available with:

```bat
.venv\Scripts\python.exe -m src.main
```

## Use

Focus the game and point to a valid map location. Press a configured hotkey or select a building in the GUI to start placing it; activate it again to stop. **Pause/Break** also stops placement. Placement pauses automatically when the game loses focus.

The default session limit is 5,000 placements. Set `max_iterations_per_session` to `0` for no limit. The game's ×5 option applies to eligible upgrades and atomic bomb salvos, not to placing five new buildings; check the in-game ×5 indicator.

## Build

On Windows, run `make.bat`. It creates `dist\OpenFrontAutoPlacer.exe`. Run the executable from a writable folder so it can create `config.toml` beside itself.

## Tests

Run the test suite from the project folder:

```bat
.venv\Scripts\python.exe -m unittest discover -s tests
```

Tests mock system input. Verify game interaction and executable builds on Windows.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and contribution guidelines.

## Disclaimer

This is an unofficial community tool. Use it only where automation is permitted by the game's rules.
