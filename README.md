# OpenFront auto-placer

Windows tool for the Steam `OpenFront.exe`. It provides a lightweight GUI and
retains the console mode. Both send a building
shortcut followed by a left click at the **current mouse position** while the
game is the foreground window. It does not bring the game to the foreground.

## Install and run

Requires Windows 10/11 and Python 3.11+ for source installation. Download the
source, open a terminal in its directory, then run:

```bat
py -3 -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m src.gui_main
```

The first launch copies `config.toml.default` to `config.toml` alongside the
source. The GUI loads and saves it automatically. Match the `game_key` values
to your in-game bindings. The original console mode remains available with
`.venv/Scripts/python.exe -m src.main`.

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
double_press_delay_ms = 20
max_iterations_per_session = 5000
log_level = "INFO"

[shortcuts]
city = { hotkey = "F1", game_key = "1", multiplier = 5 }
```

Hotkeys may use one trigger letter, digit, F1–F12, `Esc` or `Pause` with
`Ctrl`, `Shift`, and/or `Alt` (for example `Ctrl+Shift+V`). The trigger
must not overlap any in-game key. F0 does not exist on a standard keyboard,
so M.I.R.V. defaults to F10. All ten entries are required.
`double_press_delay_ms` is waited after every key press, including the
last one before the click, so the game can register the selection. It is
required and may not go below 10 ms; the template ships 300 ms.

### `multiplier`: what ×5 really does

`multiplier` mirrors the game's own ×1/×5 toggle and accepts exactly `1` or
`5`. With `multiplier = 5` the tool sends **key, key, click** — nothing else,
because any key that drops the current selection also discards the click the
game is still holding back while it validates the preview.

**×5 never places five new buildings.** OpenFront attaches the amount to an
*upgrade* intent, or to an Atomic Bomb salvo. Anywhere else the amount is
simply not sent, and the game builds exactly one structure. So `multiplier =
5` is only meaningful for City, Factory, Port, Missile Silo and S.A.M.
Launcher — and only with the pointer on an existing one of yours that can
still be upgraded, where it buys five levels at once — or for the Atomic
Bomb, where it fires five missiles. `5` is rejected for any other building.

Check the in-game **×5 badge** on the ghost's cost label: if it does not
appear, the game is not in ×5 mode and a click would only build one.

Set `log_level = "DEBUG"` to log every simulated step (`[SEND] Touche 1
(1/2)`, `[SEND] Touche 1 (2/2, arme le x5)`, `[SEND] Clic gauche`) and
confirm what was actually sent.

The click interval can be lowered to 10 ms; very short intervals may cause the
game to miss inputs. The session stops after 5000
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
- `multiplier = 5` still placing one at a time? The game only multiplies an
  upgrade or an Atomic Bomb salvo, so point at an existing structure of yours
  that can still be upgraded; on empty ground ×5 is impossible in OpenFront
  itself. Switch to `log_level = "DEBUG"` to confirm both key presses are
  sent, and watch for the in-game ×5 badge on the ghost's cost label.
- Can't create `config.toml`? Move the executable to a writable folder.
- Config error? Correct the value reported in the console or restore the
  template and restart.
- No Pause/Break key? Use the same toggle hotkey to stop, or Ctrl+C in the
  console. The worker checks for stop between actions and waits are interruptible.

Use at your own risk. Check the game's current rules before using automation.
