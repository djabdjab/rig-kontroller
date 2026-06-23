# Rig Kontrol 3 MIDI Bridge

Custom USB HID → MIDI bridge for the Native Instruments Rig Kontrol 3 on modern macOS. NI killed driver support, so we reverse-engineered the USB protocol and built a userspace bridge.

## What It Does
- Reads raw USB HID data from the Rig Kontrol 3
- Creates a virtual CoreMIDI port ("Rig Kontrol 3") visible to any DAW
- 8 footswitches → MIDI notes (or CCs)
- Expression pedal → MIDI CC

## What It Doesn't Do
- Audio interface — this bridge is MIDI-only; use your Focusrite for audio. The RK3's audio is a vendor-class isochronous USB stream, **but it is not undocumented**: NI's "caiaq" protocol is reverse-engineered and open-source in the Linux kernel (`sound/usb/caiaq/`), and the RK3 is in its device table. A userspace macOS audio bridge is a real (large) project, not a dead end — see [`CAIAQ_AUDIO.md`](CAIAQ_AUDIO.md).

## Location
`~/rig-kontroller/`

## Install
```bash
cd ~/rig-kontroller && ./install.sh
```
This installs `libusb` (via Homebrew), creates an isolated virtualenv with the
Python deps, and drops a `rig-kontroller` command into `~/.local/bin` (which
must be on your `PATH`). Nothing touches system Python.

## Usage
Once installed, run it from anywhere in the terminal:
```bash
rig-kontroller              # run the bridge
rig-kontroller --calibrate  # calibrate expression-pedal range
rig-kontroller --debug      # dump raw USB packets (verify byte offsets)
rig-kontroller --config     # show config file location + contents
```

## Auto-start at login (optional)
A macOS LaunchAgent is included so the bridge starts on login and restarts on
crash/re-plug:
```bash
cp ~/rig-kontroller/com.djabdjab.rigkontrol3.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.djabdjab.rigkontrol3.plist
```

## Ableton Setup
1. Start the bridge script
2. Settings → Link, Tempo & MIDI
3. Under Input Ports, enable **Track** and **Remote** for "Rig Kontrol 3"
4. **Cmd+M** to enter MIDI Map mode → click any parameter → stomp a footswitch

## Default Mapping
| Control | MIDI Message | Default |
|---------|-------------|---------|
| SW1 | Note 60 (C4) | Map to effect toggle, looper, etc. |
| SW2 | Note 61 | |
| SW3 | Note 62 | |
| SW4 | Note 63 | |
| SW5 | Note 64 | |
| SW6 | Note 65 | |
| SW7 | Note 66 | |
| SW8 | Note 67 | |
| Pedal | CC 11 (Expression) | Wah, volume, filter sweep |

Edit `~/rig-kontroller/config.json` to change any mapping. Set `"note": null, "cc": 64` on a button to send CC instead of notes.

## USB Protocol (reversed)
- **VID:** `0x17CC` / **PID:** `0x1940` (confirmed via IORegistry; cross-checked against `Timebutt/rig-kontrol-web`)
- Reads on EP `0x81` IN. Two packet shapes:
  - **Long packet (33 bytes)** — carries the expression-pedal ADC; `byte[0]` is `0x03` (idle) or `0x04` (button event).
  - **Short packet (8 bytes)** — button event on some firmware/OS paths.
- `byte[1]`: button bitmask (`0x01`=SW1, `0x02`=SW2, `0x04`=SW3, `0x08`=SW4, `0x10`=SW5, `0x20`=SW6, `0x40`=SW7, `0x80`=SW8, `0x00`=release)
- `byte[5:6]`: pedal ADC — **16-bit big-endian**, travel ~0–600 (run `--calibrate` for your unit).
  - ⚠️ Earlier notes read this as `byte[6:7]` little-endian and saw a pinned `~1024–1276` range. That was a bug: it captured `byte[7]` (the `0x04` type marker) as the high byte. Use `--debug` to verify the offset on hardware.

## Pedalboard Idea
Load effects on a track, map each footswitch to toggle an effect on/off:
- SW1 → Overdrive
- SW2 → Delay
- SW3 → Reverb
- SW4 → Chorus
- Pedal → Wah frequency / filter cutoff
- SW5 → Looper multi-button (record/overdub/play)
- SW6 → Looper undo
- SW7 → Looper clear
