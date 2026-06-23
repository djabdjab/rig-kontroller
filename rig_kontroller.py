#!/usr/bin/env python3
"""
Rig Kontrol 3 → MIDI Bridge
Reads USB HID from Native Instruments Rig Kontrol 3 and outputs
MIDI via a virtual CoreMIDI port visible to any DAW.

Usage:
    python rig_kontrol_midi.py              # run with defaults
    python rig_kontrol_midi.py --config     # edit mapping config
    python rig_kontrol_midi.py --calibrate  # calibrate pedal range
    python rig_kontrol_midi.py --debug      # dump raw USB packets (offset check)
"""

import usb.core
import usb.util
import rtmidi
import json
import signal
import sys
import time
from pathlib import Path

VID = 0x17CC
PID = 0x1940
CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "midi_channel": 1,
    "pedal": {
        "cc": 11,  # Expression
        # ADC lives at byte[5:6] big-endian (~0-600 travel). Run --calibrate
        # to capture YOUR device's exact range, then these get overwritten.
        "min_raw": 70,
        "max_raw": 600,
        "invert": False
    },
    "buttons": {
        "1": {"note": 60, "cc": None},   # SW1 → C4
        "2": {"note": 61, "cc": None},   # SW2 → C#4
        "3": {"note": 62, "cc": None},   # SW3 → D4
        "4": {"note": 63, "cc": None},   # SW4 → D#4
        "5": {"note": 64, "cc": None},   # SW5 → E4
        "6": {"note": 65, "cc": None},   # SW6 → F4
        "7": {"note": 66, "cc": None},   # SW7 → F#4
        "8": {"note": 67, "cc": None}    # SW8 → G4
    }
}

BUTTON_BITS = {
    1: 0x01, 2: 0x02, 3: 0x04, 4: 0x08,
    5: 0x10, 6: 0x20, 7: 0x40, 8: 0x80
}

# --- USB packet layout (corroborated against Timebutt/rig-kontrol-web WebHID) ---
# The expression-pedal ADC rides in the long (33-byte) packet as a 16-bit
# BIG-ENDIAN value at byte[5:6]. Buttons arrive either in a short (8-byte)
# packet or in a long packet flagged with byte[0] == 0x04; the bitmask is at
# byte[1] in both. Reading the pedal from byte[6:7] little-endian (the old
# bug) captured byte[7] — the 0x04 type marker — as the high byte, which is
# why the previous "raw" range was pinned at ~1024-1276.
PACKET_PEDAL_LEN = 33   # long packet carrying the pedal ADC
PACKET_BUTTON_LEN = 8   # short packet carrying a button event
PEDAL_HI = 5            # ADC high byte
PEDAL_LO = 6            # ADC low byte
BUTTON_FLAG = 0x04      # byte[0] marker for a button event in a long packet


def parse_pedal(data):
    """16-bit big-endian expression-pedal ADC from a long packet."""
    return (data[PEDAL_HI] << 8) | data[PEDAL_LO]


def load_config():
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            return json.load(f)
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG


def save_config(cfg):
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(cfg, f, indent=2)


def find_device():
    dev = usb.core.find(idVendor=VID, idProduct=PID)
    if dev is None:
        print("Rig Kontrol 3 not found. Is it plugged in?")
        sys.exit(1)
    return dev


def scale_pedal(raw, cfg):
    p = cfg["pedal"]
    lo, hi = p["min_raw"], p["max_raw"]
    val = max(lo, min(hi, raw))
    scaled = int((val - lo) / (hi - lo) * 127)
    if p.get("invert"):
        scaled = 127 - scaled
    return scaled


def calibrate():
    print("=== Pedal Calibration ===")
    print("Rock the expression pedal fully in both directions.")
    print("Press Ctrl+C when done.\n")

    dev = find_device()
    dev.set_configuration()
    usb.util.claim_interface(dev, 0)

    min_val, max_val = 99999, 0
    try:
        while True:
            try:
                data = bytes(dev.read(0x81, 512, timeout=500))
                # Only the long packet carries the pedal ADC; skip button packets.
                if len(data) != PACKET_PEDAL_LEN:
                    continue
                val = parse_pedal(data)
                if val < min_val:
                    min_val = val
                if val > max_val:
                    max_val = val
                print(f"\r  Current: {val:5d}  Range: {min_val}-{max_val}  (MIDI: 0-127 mapped)", end="")
            except usb.core.USBTimeoutError:
                pass
    except KeyboardInterrupt:
        pass
    finally:
        usb.util.release_interface(dev, 0)

    print(f"\n\nCalibrated range: {min_val} to {max_val}")
    cfg = load_config()
    cfg["pedal"]["min_raw"] = min_val
    cfg["pedal"]["max_raw"] = max_val
    save_config(cfg)
    print(f"Saved to {CONFIG_PATH}")


def run_bridge():
    cfg = load_config()
    ch = cfg["midi_channel"] - 1  # MIDI channels are 0-indexed internally

    # Setup MIDI output
    midi_out = rtmidi.MidiOut()
    midi_out.open_virtual_port("Rig Kontrol 3")
    print("Virtual MIDI port: 'Rig Kontrol 3'")

    # Setup USB
    dev = find_device()
    dev.set_configuration()
    usb.util.claim_interface(dev, 0)
    print(f"Connected: {dev.manufacturer} {dev.product}")
    print(f"MIDI Channel: {cfg['midi_channel']}")
    print(f"Pedal → CC{cfg['pedal']['cc']}  |  Buttons → Notes {cfg['buttons']['1']['note']}-{cfg['buttons']['8']['note']}")
    print("\nBridge active. Ctrl+C to quit.\n")

    prev_buttons = 0
    prev_pedal = -1
    prev_pedal_raw = 0
    pedal_deadzone = 2  # ignore ADC jitter

    def cleanup(*_):
        print("\nShutting down...")
        usb.util.release_interface(dev, 0)
        midi_out.close_port()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    while True:
        try:
            data = bytes(dev.read(0x81, 512, timeout=500))
        except usb.core.USBTimeoutError:
            continue
        except usb.core.USBError as e:
            print(f"USB Error: {e}")
            break

        n = len(data)
        if n == 0:
            continue
        msg_type = data[0]

        # --- Pedal (CC) --- only the long packet carries the ADC, so reading
        # it from a short button packet (the old bug) is impossible here.
        if n == PACKET_PEDAL_LEN:
            raw_pedal = parse_pedal(data)
            pedal_val = scale_pedal(raw_pedal, cfg)
            if pedal_val != prev_pedal:
                # Deadzone on the raw ADC suppresses jitter near a threshold.
                if prev_pedal < 0 or abs(raw_pedal - prev_pedal_raw) >= pedal_deadzone:
                    midi_out.send_message([0xB0 | ch, cfg["pedal"]["cc"], pedal_val])
                    prev_pedal = pedal_val
                    prev_pedal_raw = raw_pedal

        # --- Buttons --- bitmask at byte[1]; arrives as a short packet or a
        # long packet flagged 0x04.
        if n == PACKET_BUTTON_LEN or (n == PACKET_PEDAL_LEN and msg_type == BUTTON_FLAG):
            btn_mask = data[1]
            for btn_num, bit in BUTTON_BITS.items():
                btn_cfg = cfg["buttons"].get(str(btn_num))
                if not btn_cfg:
                    continue

                was_pressed = prev_buttons & bit
                is_pressed = btn_mask & bit

                if is_pressed and not was_pressed:
                    if btn_cfg.get("note") is not None:
                        midi_out.send_message([0x90 | ch, btn_cfg["note"], 127])
                        print(f"  SW{btn_num} ON  -> Note {btn_cfg['note']}")
                    if btn_cfg.get("cc") is not None:
                        # If cc_value is set, send that fixed value (selector mode).
                        # Otherwise default to 127 on press.
                        val = btn_cfg.get("cc_value", 127)
                        midi_out.send_message([0xB0 | ch, btn_cfg["cc"], val])
                        if btn_cfg.get("cc_value") is not None:
                            print(f"  SW{btn_num}      -> CC{btn_cfg['cc']} val {val}")

                elif was_pressed and not is_pressed:
                    if btn_cfg.get("note") is not None:
                        midi_out.send_message([0x80 | ch, btn_cfg["note"], 0])
                        print(f"  SW{btn_num} OFF -> Note {btn_cfg['note']}")
                    # Selector mode (cc_value set) = press-only, no release message.
                    if btn_cfg.get("cc") is not None and btn_cfg.get("cc_value") is None:
                        midi_out.send_message([0xB0 | ch, btn_cfg["cc"], 0])

            prev_buttons = btn_mask


def debug_dump():
    """Dump raw USB packets so byte offsets can be confirmed on real hardware.

    Stomp each switch and rock the pedal. The 'ped_be@5' column (the fix)
    should sweep cleanly ~0-600; the 'old_le@6' column (the old bug) stays
    pinned near 1024-1276 because it reads the 0x04 type marker as its high
    byte. The packet-length tally at the end shows whether buttons arrive in
    short (8-byte) or long (33-byte) packets on your device.
    """
    print("=== Raw packet debug ===")
    print("Stomp each switch and rock the pedal fully. Ctrl+C to stop.\n")
    dev = find_device()
    dev.set_configuration()
    usb.util.claim_interface(dev, 0)

    seen_lens = {}
    try:
        while True:
            try:
                data = bytes(dev.read(0x81, 512, timeout=500))
            except usb.core.USBTimeoutError:
                continue
            n = len(data)
            seen_lens[n] = seen_lens.get(n, 0) + 1
            be5 = (data[5] << 8) | data[6] if n > PEDAL_LO else -1
            le6 = (data[6] | (data[7] << 8)) if n > 7 else -1
            hexs = " ".join(f"{b:02x}" for b in data[:12])
            print(f"len={n:2d} b0={data[0]:02x} b1={data[1]:02x} "
                  f"[{hexs} ...]  ped_be@5={be5:5d}  old_le@6={le6:5d}")
    except KeyboardInterrupt:
        print(f"\n\nPacket lengths seen (len: count): {seen_lens}")
    finally:
        usb.util.release_interface(dev, 0)


if __name__ == "__main__":
    if "--calibrate" in sys.argv:
        calibrate()
    elif "--debug" in sys.argv:
        debug_dump()
    elif "--config" in sys.argv:
        cfg = load_config()
        print(f"Config at: {CONFIG_PATH}")
        print(json.dumps(cfg, indent=2))
        print("\nEdit the file directly to change mappings.")
    else:
        run_bridge()
