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

## Build steps (one-time)
Assemble it once, then **Save as a Rack Preset** — it reloads in any GR instance forever after.

**Prep**
1. Start the bridge: `rig-kontroller` (with `config.bass-wobble.json` loaded). This creates the "Rig Kontrol 3" MIDI port.
2. Guitar Rig → **Preferences → MIDI** → enable **"Rig Kontrol 3"** as a controller input (standalone). In a DAW the plugin gets MIDI from its host track instead.

**Build the chain** (drag from the Components browser, top → bottom)
3. **Noise Gate** — threshold just high enough to kill input hiss.
4. **VC 76** comp — moderate; Expert panel **Dry ~30%** (parallel).
5. **Harmonic Synthesizer** — set the **Guitar/Bass switch to BASS** (toggled later by SW4).
6. **Oktaver** — Oct 1 up, Oct 2 down, Dry full (toggled by SW3).
7. **Crossover** (Tools) — split **~130 Hz**. Leave the **LOW** lane empty (clean); into the **HIGH** lane drag **Skreamer → Pro-Filter**. Put those two in a **Container** so SW1 can toggle the whole wobble block.
8. **Pro-Filter:** Mode **LP**, Slope **24 dB**, Res **~75%**, Freq **~35%**.
9. (after the Crossover) **Replika** or **Twin Delay** — **Sync ON**, 1/8-dotted to taste (toggled by SW6).
10. **Preset Volume** last — the pedal's swell target.

**The wobble engine**
11. Add a **Step Sequencer** modifier (gated) and/or an **LFO** modifier (smooth). **Tempo Sync ON**; Step Seq = 1/16, LFO = 1/8.
12. **Drag the modifier's assignment icon onto Pro-Filter → Freq.** In the Expert panel set the **modulation depth** (~50%, taste up).
13. For SW5 (SHAPE): assign *both* an LFO and a Step Seq to Freq and toggle which is active — or toggle the LFO waveform sine↔square.

**The 8 Macro buttons**
14. In the rack **Macros** section, create 8 **Macro buttons**, each in **Toggle** mode.
15. Assign each to its target's **on/off (bypass)**: M1→WOBBLE container · M2→wobble rate · M3→Oktaver · M4→Harmonic Synth · M5→shape · M6→delay · M7→Skreamer drive boost · M8→**Metronome Tap**. For M2/M7 use the Macro's Off/On values + Min/Max to set the two states.
16. **MIDI-Learn each Macro:** right-click the Macro → **Learn MIDI Control** → stomp the matching RK3 switch (SW1→M1 … SW8→M8). CC 20–27 land automatically.

**The SPACE pedal**
17. Make a **Macro knob** named "SPACE." Right-click → **Learn MIDI Control** → rock the RK3 pedal (CC 11).
18. Assign SPACE to **Pro-Filter Freq** (Min/Max: heel = dark, toe = open) **and** to **Preset Volume** (heel = lower, toe = unity/louder). One pedal opens the filter and pushes into The Room.

**Tempo · test · save**
19. Set the **Metronome BPM** to your tune (or tap SW8). Synced modifiers + delay follow it.
20. Stomp SW1, ride the pedal — confirm the wobble tracks and the sweep is clean.
21. **Save as a Rack Preset** → "BASS — Wobble/Ether." One click reloads it from then on.

## Playing the two poles
- **Wobble / dub:** SW1 on, SW3 sub on, ride the pedal; SW2 for double-time drops, SW5 smooth↔gated, SW8 to tap tempo, SW6 for clocked echoes. On the board: **Zeus fuzz** for grit, **Zeus octave OFF** (don't fight GR's Oktaver), Muff for the huge feature fuzz.
- **Ethereal / FACS:** SW4 synth on, SW1 off (or a slow LFO), feather the pedal to swell into **Room → flanger → Joyo**; Tensor does reverse/drones. Let the board's free-running ambience breathe.

## Board pairing notes
- **Don't run Zeus octave and GR Oktaver together** — stacked octave-downs phase-fight.
- Joyo delay / Classic Flanger / Tensor **won't follow** SW8 tempo — only Guitar Rig locks.
- For clocked dub, use GR's synced delay (SW6); leave the Joyo for free-running texture / self-oscillation.

See the per-pedal references in Carlton's Brain → `Hardware Rig/`.
