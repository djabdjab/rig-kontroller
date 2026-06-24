# RIG — Bass Wobble / Ether Setup

How the Rig Kontrol 3 + Guitar Rig 6 (the "rig-kontroller" setup) drives a physical bass pedalboard — from dubstep wobble to FACS-style ethereal drones. This is the playable spec; load [`config.bass-wobble.json`](config.bass-wobble.json) onto the RK3 and build the Guitar Rig rack below.

## Signal flow
The "rig-kontroller" is the **source**, feeding the analog board:
```
Bass ─▶ Scarlett IN ─▶ GUITAR RIG 6 ─▶ Scarlett OUT ─▶ [reamp/level box] ─▶ PEDALBOARD:
        (synced wobble, synth, sub,                       PolyTune ─▶ Red Witch Zeus ─▶ Big Muff
         saturate-before-filter)                            ─▶ Tensor ─▶ Blood Moon (phaser)
                                                             ─▶ The Room ─▶ Classic Flanger
   Rig Kontrol 3 ──USB MIDI──▶ Guitar Rig                   ─▶ Joyo Analog Delay ─▶ Amp (Ampeg)
```
- **Guitar Rig** does the clock-locked work (the only synced voice). **Board** does dirt + the ambient tail.
- A **reamp/level box** drops the Scarlett's line output to instrument level so the fuzzes behave. Set **PolyTune to buffered** when fed post-reamp.

## Guitar Rig 6 rack — "BASS — Wobble/Ether"
One master rack (no preset-switching mid-song), hosted as a **Guitar Rig 6 plugin in Ableton Live** (preset **"Rig Kontroller Bass Rack"** on the bass track). The 8 RK3 pods send **Notes** that toggle GR parameters directly via Ableton MIDI-map; the pedal sends **CC 11** to sweep Freq + Volume.
```
Input
→ Noise Gate                          (light)
→ VC 76 comp  (Dry ~30% = parallel)   (even level into pitch tracking)
→ [Harmonic Synthesizer — BASS mode]  ← pod 4  (synth-bass voice)
→ [Oktaver — Oct1]                    ← pod 3  (clean sub)
→ Crossover  (split ~130 Hz)
     LOW band  → clean through                 (fundamental + sub stay solid)
     HIGH band → Skreamer ─▶ Pro-Filter        ← THE WOBBLE (pod 1)
   (recombine)
→ [Replika Shimmer — Tempo Sync] ← pod 6 echo / pod 5 bloom   (clocked dub echoes + ether tail the Joyo can't do)
→ Volume                               (the pedal's swell target)
→ Output → reamp → board
```

### Building the wobble
1. **Pro-Filter:** Mode **LP**, Slope **full 4-Pole** (= 24 dB/oct; the knob blends 2-Pole/4-Pole, so turn it fully to 4-Pole), Res ≈ **75%**, base Freq ≈ **35%**.
2. Drop an **LFO** modifier onto **Pro-Filter → Freq**. Waveform **Random** (the `◀ ▶` selector — generative/glitchy on purpose), **Tempo Sync ON**, rate **1/8** or **1/16** (pod 2 re-clocks it), depth high. *(No Step Sequencer — Random is the shape; change the waveform by hand on that selector if you want a smooth sweep.)*
3. Light **Skreamer before it** supplies the harmonics the filter chews (board dirt is downstream, so make grit in-the-box for the wobble).
4. **Expression pedal also → Pro-Filter Freq:** the pedal moves the *center* cutoff while the modifier wobbles *around* it → play the wobble with your foot, in tempo.

### Set tempo
**Ableton's tempo** drives everything synced — the GR plugin (LFO + Replika) follows the host. Set the BPM in Ableton or tap **pod 8**. Only Guitar Rig follows this — the board's delay/flanger/Tensor free-run (by design).

## Rig Kontrol 3 map ([`config.bass-wobble.json`](config.bass-wobble.json))
The RK3 reaches Ableton through the bridge's virtual MIDI port "Rig Kontrol 3". **Pods send Notes, not CC** — a Note mapped to a plugin parameter in Ableton *toggles* it on each press (CC just latches on, since the switch never sends a release). The pedal stays **CC 11** (continuous). One quirk of this unit: its physical pods are **rotated +4** from the bridge's internal button index — the config compensates, so physical pod 1 really is WOBBLE.

| Pod | Note | Function | Ableton target |
|-----|------|----------|----------------|
| 1 | C3 | **WOBBLE** | Skreamer + Pro-Filter on/off (toggled together) |
| 2 | C#3 | **RATE ×2** | LFO Rate — Min/Max = 1/8 ↔ 1/16 |
| 3 | D3 | **SUB** | Oktaver on/off |
| 4 | D#3 | **SYNTH** | Harmonic Synthesizer on/off |
| 5 | E3 | **SHIMMER** | Replika Shimmer (+Feedback/Mix) — Min/Max low ↔ bloom |
| 6 | F3 | **DELAY** | Replika on/off |
| 7 | F#3 | **GRIT** | Skreamer Drive — Min/Max normal ↔ boosted |
| 8 | G3 | **TAP** | Ableton Tap Tempo |
| **Pedal** | CC 11 | **SPACE** | Pro-Filter Freq **+** Volume — heel = dark/quiet, toe = open/loud |

**Mapping in Ableton:** select the bass track → on the GR device hit **Configure**, then click each target control in the GR window to expose it. **Cmd+M**, click the exposed parameter, press the pod → mapped (toggles natively). For the two-state knobs (RATE / SHIMMER / GRIT) set the mapping row's **Min/Max** to the two values while in Map mode. The pedal maps as an absolute CC onto both Pro-Filter Freq and Volume (Min/Max so heel = dark/quiet, toe = open/unity — never above unity). The MIDI Mappings list (with the Min/Max columns) is only visible *while* in Map mode.

### Load the controller config
```bash
cp ~/rig-kontroller/config.bass-wobble.json ~/rig-kontroller/config.json
rig-kontroller            # then re-run --calibrate if the pedal range drifted
```

## Build steps (one-time)
Assemble it once, then **Save as a Rack Preset** — it reloads in any GR instance forever after.

**Prep**
1. Start the bridge: `cp config.bass-wobble.json config.json && rig-kontroller`. This creates the "Rig Kontrol 3" MIDI port. Run it **detached** (`nohup rig-kontroller &`) or install the LaunchAgent so it survives a reboot.
2. In **Ableton**: drop **Guitar Rig 6** as a plugin on the bass track, then Settings → **Link/Tempo/MIDI** → set **"Rig Kontrol 3" → Remote: On**. (Bridge must be running first so the port exists; reopen the pane to re-scan if the bridge restarted.)

**Build the chain** (drag from the Components browser, top → bottom)
3. **Noise Gate** — threshold just high enough to kill input hiss.
4. **VC 76** comp — moderate; Expert panel **Dry ~30%** (parallel).
5. **Harmonic Synthesizer** — set the **Guitar/Bass switch to BASS** (toggled later by pod 4 — SYNTH).
6. **Oktaver** — both voices are octave-*down*: **Oct 1 (−1) up** as the clean sub, **Oct 2 (−2) low/off** (subsonic), **Dry full** (toggled by pod 3 — SUB).
7. **Crossover** (Tools) — split **~130 Hz**. Leave the **LOW** lane empty (clean); into the **HIGH** lane drag **Skreamer → Pro-Filter**. *(No Container needed — and GR often won't nest one inside a Crossover lane anyway. Instead, map **pod 1 (WOBBLE)** to **both** the Skreamer and Pro-Filter on/off in Ableton; a Note mapped to two params toggles them together, so one stomp kills the whole wobble block and passes the highs clean.)*
8. **Pro-Filter:** Mode **LP**, Slope **full 4-Pole** (= 24 dB/oct; the knob blends 2-Pole/4-Pole, so turn it fully to 4-Pole), Res **~75%**, Freq **~35%**.
9. (after the Crossover) **Replika Shimmer** — **Sync ON**, 1/8-dotted echo to taste. Pod 6 toggles the echo; pod 5 blooms the shimmer/feedback for the ether tail. One box does dub *and* ether (Twin Delay dropped).
10. **Volume** last — the pedal's swell target.

**The wobble engine**
11. Add an **LFO** modifier. **Tempo Sync ON**, rate **1/8**, waveform **Random** (`◀ ▶` selector).
12. **Drag the LFO's assignment icon onto Pro-Filter → Freq.** In the Expert panel set the **modulation depth** (~50%, taste up).
13. *(No SHAPE switch — Random is the shape. To go smooth, change the LFO waveform by hand on the `◀ ▶` selector.)*

**Map the 8 pods in Ableton** (full how-to under the RK3 map above)
14. Select the bass track → on the GR device click **Configure** → in the GR window click each control to expose it (the on/offs for WOBBLE/SUB/SYNTH/DELAY; the Drive/Rate/Shimmer knobs for GRIT/RATE/SHIMMER) → click **Configure** off.
15. **Cmd+M**, click an exposed parameter, press its pod → mapped (Notes toggle natively). Pod 1 → Skreamer **and** Pro-Filter on/off (both to pod 1). For the two-state knobs (pods 2/5/7) set the mapping row's **Min/Max** to the two values while in Map mode.
16. **Pod 8 → TAP:** map it to Ableton's own **Tap Tempo** button (top transport bar).

**The SPACE pedal**
17. Expose **Pro-Filter Freq** and the **Volume** knob (Configure).
18. **Cmd+M** → click Pro-Filter Freq → rock the pedal (CC 11); then click Volume → rock the pedal again. Set Min/Max so **heel = dark/quiet, toe = open/unity** (never above unity). One pedal opens the filter and swells the level.

**Tempo · test · save**
19. Set the tempo in **Ableton** (or tap **pod 8**). The synced LFO + Replika follow the host tempo.
20. Stomp **pod 1**, ride the pedal — confirm the wobble tracks and the sweep is clean.
21. **Save the GR preset** → "Rig Kontroller Bass Rack." It reloads in the plugin anytime.

## Playing the two poles
- **Wobble / dub:** pod 1 on, pod 3 sub on, ride the pedal; pod 2 for double-time drops, pod 8 to tap tempo, pod 6 for clocked echoes, pod 7 GRIT into the filter. On the board: **Zeus fuzz** for grit, **Zeus octave OFF** (don't fight GR's Oktaver), Muff for the huge feature fuzz.
- **Ethereal / FACS:** pod 4 synth on, pod 1 off, **pod 5 to bloom the Replika shimmer**, feather the pedal to swell into **Room → flanger → Joyo**; Tensor does reverse/drones. The in-box shimmer now carries the tail even before the board's free-running ambience.

## Board pairing notes
- **Don't run Zeus octave and GR Oktaver together** — stacked octave-downs phase-fight.
- Joyo delay / Classic Flanger / Tensor **won't follow** pod 8 / Ableton tempo — only Guitar Rig locks.
- For clocked dub, use Replika's synced echo (pod 6); leave the Joyo for free-running texture / self-oscillation.

See the per-pedal references in Carlton's Brain → `Hardware Rig/`.
