# OpenFront auto-placer

Console-based Windows tool for the Steam `OpenFront.exe`. It sends a building
shortcut followed by a left click at the **current mouse position** while the
game is the foreground window. It does not bring the game to the foreground.

## Install and run

Requires Windows 10/11 and Python 3.11+ for source installation. Download the
source, open a terminal in its directory, then run:

```bat
py -3 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m src.main
```

The first launch copies `config.toml.default` to `config.toml` alongside the
source. Edit `config.toml` while the tool is stopped; changes persist across
restarts. Match the `game_key` values to your in-game bindings.

## Usage and configuration

Keep the console open, focus the game, and point the cursor at a valid location.
Press F1–F10 to toggle the corresponding building. Press the same key again to
stop; another building key switches modes. **Pause/Break** stops any active
mode; **Ctrl+C** in the console exits. Losing game focus or minimizing the game
pauses clicks until focus returns. If the game cannot be found, the console
prints a warning. The click is *not* tied to any target coordinate.

Example from `config.toml.default`:

```toml
[general]
click_delay_ms = 100
double_press_delay_ms = 10
max_iterations_per_session = 5000
log_level = "INFO"

[shortcuts]
city = { hotkey = "F1", game_key = "1", stackable = true, target = 1 }
```

Hotkeys may use one trigger letter, digit, F1–F12, Escape or Pause with
`Ctrl`, `Shift`, and/or `Alt` (for example `Ctrl+Shift+V`). The trigger
must not overlap any in-game key. F0 does not exist on a standard keyboard,
so M.I.R.V. defaults to F10. All ten entries are required. The `stackable`
flag must match the building: City, Factory, Port, Missile Silo, S.A.M. and
Atomic Bomb are stackable. When `target > 5`, those buildings arm the game's
×5 selection; other buildings place one at a time. `double_press_delay_ms` is
waited after every key press, including the last one before the click, so the
game can register the selection. `target` is a selection mode, **not** an
automatic stopping count.

The ×5 selection is a *toggle* in the game: pressing the building key again
switches between ×1 and ×5, and placing a building does not reset it. Sending
two presses blindly therefore lands on ×5 only when the previous state
happens to match. Each ×5 placement is consequently sent as **Escape, key,
key, click**: Escape clears any selection, so the first press always selects
×1 and the second always arms ×5.

The game applies ×5 only when it is an upgrade — the pointer must be over an
existing, upgradeable structure — or for an Atomic Bomb. On empty ground it
builds a single structure whatever the selection shows.

Game keys are sent as physical key presses, identified by their position on a
US keyboard layout, because the game reads `KeyboardEvent.code` (`Digit1`,
`KeyA`). This is layout independent: `game_key = "1"` always reaches the
game's *1* shortcut, even on AZERTY where that key types `&`.

The click interval has a minimum of 100 ms. The session stops after 5000
placements by default; set `max_iterations_per_session = 0` for no limit
(only if you accept the risk). Toggle again to start a new session.

## Build a standalone executable

On **Windows**, run `make.bat`. The PyInstaller one-file executable is
`dist\OpenFrontAutoPlacer.exe`; copy it to a writable folder and run it. It
creates `config.toml` next to the executable on first launch. No Python
installation is required to run the built executable; Windows may require
its standard Visual C++ runtime depending on the build environment.
Builds made on Linux or macOS cannot produce a Windows executable.

Run the built executable with the same privilege level as the game. Windows
input isolation can prevent global hooks or simulated events from reaching a
game running with higher privileges.

## Tests

From the project root, run `.venv\Scripts\python.exe -m unittest discover -s tests`
on Windows, or `.venv/bin/python -m unittest discover -s tests` on Linux.
System input is mocked in tests. Actual game interaction and Windows packaging
must be verified manually on a Windows machine.

## Troubleshooting and safety

- No clicks? Focus the non-minimized `OpenFront.exe` window, check your game
  bindings, pointer location, and Windows privilege level.
- Clicks logged but nothing is built? The pointer must be over the map, not
  over the HUD, and the match must be past the spawn phase. Raise
  `double_press_delay_ms` if the game needs longer to arm the selection.
- `target > 5` still placing one at a time? Point at an existing structure you
  can upgrade; the game ignores ×5 on empty ground. Raise
  `double_press_delay_ms` if the ×5 badge does not appear before the click.
- Can't create `config.toml`? Move the executable to a writable folder.
- Config error? Correct the value reported in the console or restore the
  template and restart.
- No Pause/Break key? Use the same toggle hotkey to stop, or Ctrl+C in the
  console. The worker checks for stop between actions and waits are interruptible.

Use at your own risk. Check the game's current rules before using automation.
