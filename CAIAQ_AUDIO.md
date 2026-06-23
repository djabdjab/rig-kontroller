# Rig Kontrol 3 Audio — Scoping Notes

> TL;DR: The RK3 audio path is **not** an undocumented black box. Native
> Instruments' "caiaq" USB audio protocol is fully reverse-engineered and
> open-source in the Linux kernel (`sound/usb/caiaq/`), and `RIGKONTROL3` is
> in its supported-device table. A userspace macOS audio bridge is a real,
> bounded project — large, but not a dead end. This corrects the README's
> "no driver = no audio" framing.

## Evidence

- `sound/usb/caiaq/device.c` lists `USB_PID_RIGKONTROL3` under
  `USB_VID_NATIVEINSTRUMENTS` in `snd_usb_caiaq_id_table` — the kernel binds
  `snd-usb-caiaq` to this exact VID/PID (`0x17CC` / `0x1940`).
- The same file has an RK3-specific init that writes to the unit's LED display
  ("two centered dashes") via `EP1_CMD_WRITE_IO` — so even the control surface
  quirks are documented.

## Audio format (from `sound/usb/caiaq/audio.c`)

| Property | Value |
|---|---|
| Sample format | `S24_3BE` — 24-bit signed, 3 bytes/sample, **big-endian** |
| On-wire sample | 4 bytes/sample (`BYTES_PER_SAMPLE_USB`), 24 significant bits |
| Transfer type | Isochronous URBs, `FRAMES_PER_URB = 8`, `BYTES_PER_FRAME = 512` |
| Control channel | `EP1` command writes (LED, config) |
| Max buffer | 128 KB |

This is a vendor-class (bDeviceClass `0xFF`) isochronous audio stream — **not**
USB Audio Class — which is exactly why generic macOS drivers ignore it.

## What a macOS userspace bridge would take

1. **Claim the audio interface** via libusb (separate from interface 0, which
   the MIDI bridge already claims for HID).
2. **Iso streaming**: libusb supports isochronous transfers, but you must
   manage URB-equivalent transfer pools and the 8-frame cadence yourself.
   This is the hard part — latency and xrun handling.
3. **Sample plumbing**: unpack `S24_3BE` from the 4-byte on-wire slots into
   whatever your sink wants.
4. **Expose to the OS**: feed a virtual CoreAudio device. Practical options:
   - **BlackHole** or a CoreAudio HAL plugin as the virtual endpoint, or
   - a Core Audio Server Plugin (AudioServerPlugin) you write.
5. **Send the RK3 init** (`EP1_CMD_WRITE_IO` LED sequence) so the unit enters
   streaming mode the way the kernel driver does.

## Effort & recommendation

- **High effort** (iso transfer management + CoreAudio plumbing), **low-ish
  risk** (the protocol is known; port, don't reverse-engineer).
- Translate `audio.c` URB handling → libusb iso transfers; reuse the device
  init from `device.c`.
- Realistically a separate project from the MIDI bridge. If the goal is just
  "use the RK3 as a footcontroller," the MIDI bridge already covers it and the
  Focusrite handles audio (per the README). Pursue this only if RK3-as-an-
  audio-interface is genuinely wanted.

## References

- Linux kernel: https://github.com/torvalds/linux/tree/master/sound/usb/caiaq
  - `device.c` — device table + RK3 init
  - `audio.c` — iso streaming + `S24_3BE` format
- Same-hardware projects: `rstets/rigkontrol3-linux-midicontroller` (relies on
  the kernel caiaq input events), `Timebutt/rig-kontrol-web` (WebHID, MIDI-only)
