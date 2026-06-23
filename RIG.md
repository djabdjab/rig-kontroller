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
One master rack (no preset-switching mid-song); the 8 RK3 switches toggle **Macro buttons** (Toggle mode), the pedal drives a **Macro knob**.
```
Input
→ Noise Gate                          (light)
→ VC 76 comp  (Dry ~30% = parallel)   (even level into pitch tracking)
→ [Harmonic Synthesizer — BASS mode]  ← SW4   (synth-bass voice)
→ [Oktaver — Oct1]                    ← SW3   (clean sub)
→ Crossover  (split ~130 Hz)
     LOW band  → clean through                 (fundamental + sub stay solid)
     HIGH band → Skreamer ─▶ Pro-Filter        ← THE WOBBLE
   (recombine)
→ [Replika / Twin Delay — Tempo Sync] ← SW6   (clocked dub echoes the Joyo can't do)
→ Preset Volume                        (the pedal's swell target)
→ Output → reamp → board
```

### Building the wobble
1. **Pro-Filter:** Mode **LP**, Slope **24 dB**, Res ≈ **75%**, base Freq ≈ **35%**.
2. Drag a **Step Sequencer** (gated/rhythmic) *or* **LFO** (smooth) modifier **onto Pro-Filter → Freq**. **Tempo Sync ON**, rate **1/8** or **1/16**, depth high.
3. Light **Skreamer before it** supplies the harmonics the filter chews (board dirt is downstream, so make grit in-the-box for the wobble).
4. **Expression pedal also → Pro-Filter Freq:** the pedal moves the *center* cutoff while the modifier wobbles *around* it → play the wobble with your foot, in tempo.

### Set tempo
Metronome **BPM** field, or **Tap** (mapped to SW8). Standalone can also chase external MIDI clock. Only Guitar Rig follows this — the board's delay/flanger/Tensor free-run (by design).

## Rig Kontrol 3 map ([`config.bass-wobble.json`](config.bass-wobble.json))
| Switch | CC | Macro (name in GR) | Does |
|--------|----|--------------------|------|
| SW1 | 20 | **WOBBLE** | Pro-Filter wobble section on/off |
| SW2 | 21 | **RATE ×2** | wobble rate 1/8 ↔ 1/16 |
| SW3 | 22 | **SUB** | Oktaver clean sub on/off |
| SW4 | 23 | **SYNTH** | Harmonic Synthesizer (bass) on/off |
| SW5 | 24 | **SHAPE** | wobble: smooth LFO ↔ gated Step Seq |
| SW6 | 25 | **DUB DELAY** | GR synced delay on/off |
| SW7 | 26 | **GRIT** | boost the pre-filter Skreamer |
| SW8 | 27 | **TAP** | tap tempo to the Metronome |
| **Pedal** | 11 | **SPACE** | Pro-Filter Freq **+** Preset Volume — heel = dark/quiet, toe = open/loud → swells into The Room |

**In Guitar Rig:** create a Macro button per switch (Toggle mode), MIDI-Learn it to the CC above, and assign it to the target's on/off. The RK3's CC-selector mode (one CC per press, no release) is exactly what a Toggle Macro wants. For the pedal, make a **Macro knob "SPACE"**, Learn it to CC 11, and map it (with Min/Max) to both Pro-Filter Freq and Preset Volume.

### Load the controller config
```bash
cp ~/rig-kontroller/config.bass-wobble.json ~/rig-kontroller/config.json
rig-kontroller            # then re-run --calibrate if the pedal range drifted
```

## Playing the two poles
- **Wobble / dub:** SW1 on, SW3 sub on, ride the pedal; SW2 for double-time drops, SW5 smooth↔gated, SW8 to tap tempo, SW6 for clocked echoes. On the board: **Zeus fuzz** for grit, **Zeus octave OFF** (don't fight GR's Oktaver), Muff for the huge feature fuzz.
- **Ethereal / FACS:** SW4 synth on, SW1 off (or a slow LFO), feather the pedal to swell into **Room → flanger → Joyo**; Tensor does reverse/drones. Let the board's free-running ambience breathe.

## Board pairing notes
- **Don't run Zeus octave and GR Oktaver together** — stacked octave-downs phase-fight.
- Joyo delay / Classic Flanger / Tensor **won't follow** SW8 tempo — only Guitar Rig locks.
- For clocked dub, use GR's synced delay (SW6); leave the Joyo for free-running texture / self-oscillation.

See the per-pedal references in Carlton's Brain → `Hardware Rig/`.
