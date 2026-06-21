# Rig Kontrol 3 MIDI Bridge

Custom USB HID → MIDI bridge for the Native Instruments Rig Kontrol 3 on modern macOS. NI killed driver support, so we reverse-engineered the USB protocol and built a userspace bridge.

## What It Does
- Reads raw USB HID data from the Rig Kontrol 3
- Creates a virtual CoreMIDI port ("Rig Kontrol 3") visible to any DAW
- 8 footswitches → MIDI notes (or CCs)
- Expression pedal → MIDI CC

## What It Doesn't Do
- Audio interface — the RK3's audio uses a proprietary vendor-class USB protocol. No driver = no audio. Use your Focusrite for that.

## Location
`~/rig-kontrol-midi/`

## Dependencies
```bash
pip3 install hidapi python-rtmidi pyusb
brew install libusb
```

## Usage
```bash
# Run the bridge
python3 ~/rig-kontrol-midi/rig_kontrol_midi.py

# Calibrate expression pedal range
python3 ~/rig-kontrol-midi/rig_kontrol_midi.py --calibrate

# View/edit config
python3 ~/rig-kontrol-midi/rig_kontrol_midi.py --config
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

Edit `~/rig-kontrol-midi/config.json` to change any mapping. Set `"note": null, "cc": 64` on a button to send CC instead of notes.

## USB Protocol (reversed)
- **VID:** `0x17CC` / **PID:** `0x1940`
- 33-byte packets on EP 0x81 IN (bulk)
- `byte[0]`: `0x03` = idle, `0x04` = button event
- `byte[1]`: button bitmask (`0x01`=SW1, `0x02`=SW2, `0x04`=SW3, `0x08`=SW4, `0x10`=SW5, `0x20`=SW6, `0x40`=SW7, `0x80`=SW8, `0x00`=release)
- `byte[6:8]`: pedal ADC (16-bit little-endian, range ~1024–1276)

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
