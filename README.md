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
double_press_delay_ms = 20
max_iterations_per_session = 5000
log_level = "INFO"

[shortcuts]
city = { hotkey = "F1", game_key = "1", stackable = true, multiplier = 1 }
```

Hotkeys may use one trigger letter, digit, F1–F12, `Esc` or `Pause` with
`Ctrl`, `Shift`, and/or `Alt` (for example `Ctrl+Shift+V`). The trigger
must not overlap any in-game key. F0 does not exist on a standard keyboard,
so M.I.R.V. defaults to F10. All ten entries are required. The `stackable`
flag must match the building: City, Factory, Port, Missile Silo, S.A.M. and
Atomic Bomb are stackable — these are the only ones the game can place in
bulk. `double_press_delay_ms` is waited after every key press, including the
last one before the click, so the game can register the selection. It is
required and may not go below 10 ms; the template ships 20 ms.

### Placing five at a time (`multiplier`)

`multiplier` is the selection size, **not** an automatic stopping count. It
accepts exactly `1` or `5`, mirroring the game's own ×1/×5 toggle, and `5` is
only allowed on a stackable building. Escape may not be a hotkey trigger when
any building uses `multiplier = 5`, because the sequence sends Escape itself:

```toml
city = { hotkey = "F1", game_key = "1", stackable = true, multiplier = 5 }
```

With `multiplier = 5` the tool sends **Escape, key, key, click**. The game
arms ×5 on a *second consecutive* press of the building key, so it only works
starting from no selection; Escape guarantees that, because a click whose
preview has not resolved yet is deferred by the game and can otherwise leave
the previous selection standing and invert the pair.

**The game applies ×5 only to an upgrade or to an Atomic Bomb.** The pointer
must sit on (or next to) an existing structure of the same type that you own
and can still upgrade. On empty ground the game silently discards the
multiplier and builds a single structure — that is the game's behaviour, not
a limitation of this tool. Check the in-game **×5 badge** above the ghost
preview: if it does not appear, the game is not in ×5 mode.

Set `log_level = "DEBUG"` to log every simulated step (`[SEND] Échap`,
`[SEND] Touche 1 (1/2)`, `[SEND] Touche 1 (2/2, arme le x5)`, `[SEND] Clic
gauche`) and confirm what was actually sent.

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
- `multiplier = 5` still placing one at a time? Point at an existing structure
  of the same type that you own and can still upgrade; the game ignores ×5 on
  empty ground. Switch to `log_level = "DEBUG"` to confirm both key presses
  are sent, and watch for the in-game ×5 badge above the ghost preview.
- Can't create `config.toml`? Move the executable to a writable folder.
- Config error? Correct the value reported in the console or restore the
  template and restart.
- No Pause/Break key? Use the same toggle hotkey to stop, or Ctrl+C in the
  console. The worker checks for stop between actions and waits are interruptible.

Use at your own risk. Check the game's current rules before using automation.
