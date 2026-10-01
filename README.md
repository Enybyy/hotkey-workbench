# Hotkey Workbench

Windows keyboard/mouse sequences with an AutoHotkey v2 implementation, a Python engine, and an interactive browser preview.

[![Actual browser preview](assets/demo-desktop.png)](https://enybyy.github.io/hotkey-workbench/)

[Try the demo](https://enybyy.github.io/hotkey-workbench/) · [Download the AutoHotkey script](HotkeyWorkbench.ahk)

## Run on Windows

Install [AutoHotkey v2](https://www.autohotkey.com/) and open `HotkeyWorkbench.ahk`. The control panel starts in **preview mode**: actions appear in the log without generating mouse/keyboard output. To use the original game profile, uncheck preview and bring `left4dead2.exe` to the foreground.

| Key | Sequence | Requested delays |
| --- | --- | --- |
| Q | Wheel down 2 → wheel up 2 | 31 / 32 ms |
| T | Left click → right click | 100 ms |
| 1 | Left click → right click → Space | 10 / 10 / 20 ms |
| F8 | Pause / resume | Panel or target window |
| Alt+F5 | Exit | Panel or target window |

The panel's preview buttons always preview, even when live mode is selected. Hotkeys pass through to other windows. A held shortcut runs once; cooldown and busy state prevent overlapping sequences. Pause, mode changes and target focus loss cancel remaining steps. Windows timers do not guarantee exact millisecond execution.

## How it works

1. A key selects a declared sequence.
2. The engine checks pause, cooldown and target focus.
3. Each action runs in order; a one-shot timer schedules the next step.
4. Each callback rechecks cancellation and focus before sending input.
5. The bounded event log explains the result; closing the panel ends the process.

The browser demo visualizes these steps within the page. It supports slow motion, pause, cancellation and JSON export. It cannot send input to a game or operate other applications.

## Python version

```powershell
python hotkeys.py --demo 1
python -m pip install -r requirements.txt
python hotkeys.py --live
```

Dry-run mode needs only the standard library. Live mode uses `pynput`; output is limited to a foreground window titled Left 4 Dead 2. The Python listener does not suppress the original shortcut key. The AutoHotkey profile uses the executable name and intercepts the active shortcuts. Choose the implementation that matches the application.

## Changes from the original

This project derives from an existing Python/pynput L4D2 hotkey script. Its three action sequences are retained, with `1` correctly replacing the original accidental `|` mapping. It adds pause, bounded execution, overlap protection, cancellation, target checks and a shutdown path that terminates the main listener. An AutoHotkey v2 port and visible browser preview make the sequence inspectable.

## Verification

```powershell
python -m unittest discover -s tests -v
AutoHotkey64.exe /ErrorStdOut HotkeyWorkbench.ahk --self-test
```

Five Python tests cover action order, corrected mapping, cooldown, focus loss, cancellation and overlap/pause. AutoHotkey v2.0.28 successfully loaded the complete script and checked its configuration in self-test mode. The browser preview was exercised for the three-step sequence and pause/resume; its narrow layout was checked at the browser's effective 400px viewport.

Native gameplay and compatibility with a client's particular game/script have **not** been tested. The AutoHotkey check validates loading/configuration, not every live execution path. See [verification notes](docs/VERIFICATION.md).

## Customize

Edit `Target` and `Sequences` in the `.ahk` file for the intended application. Check whether an existing client script uses AutoHotkey v1 or v2 before modifying it; the syntax differs. The profile contains finite sequences only. Use it in applications where input automation is permitted.
