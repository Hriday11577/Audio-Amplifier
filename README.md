# 🔊 Everyday Audio Enhancer

> Class AB Audio Amplifier · PCB-assembled · 2N5484 JFET input stage · BD139/BD140 push-pull output

Fourth Semester MP Project — Electronics and Communication Engineering, MIT Manipal (JAN/MAY 2024)

**Team:** Aditi Javeri (220907706) · Anish Singhal (220907714) · Hriday Raizada (220907716)

---

## Overview

A three-stage audio amplifier assembled on a universal PCB, capable of amplifying a 100 mV audio input to a usable output level across an 8 Ω / 1.5 W speaker. The design uses a Class AB output stage for low crossover distortion, a regulated 10 V pre-amp supply for stable biasing, and a negative feedback loop for thermal stability.

**Measured performance:**

| Parameter | Value |
|---|---|
| Input voltage | 100 mV |
| Output voltage | 240 mV |
| Voltage gain | 2.4× (≈ 7.6 dB) |
| Load | 8 Ω speaker |
| Supply | 18 V (9 V regulated for pre-amp) |
| Output stage class | AB |

---

## Circuit Architecture

```
Audio In (100 mV)
     │
    [C1] coupling cap
     │
    [VR1] 1 MΩ volume pot (log taper)
     │
┌────▼────────────────────────────────────────────────────┐
│  STAGE 1 – 2N5484 JFET                                 │
│  High input impedance (~1 MΩ), common-source config     │
│  Drain load: R1 (68 kΩ)   Source: R2 (1.8 kΩ)         │
└────────────────────┬────────────────────────────────────┘
                     │ [C2] AC coupling
┌────────────────────▼────────────────────────────────────┐
│  STAGE 2 – BC548 NPN common-emitter                     │
│  Voltage gain stage. VR2 (10 kΩ) sets quiescent point  │
│  C8 (470 µF) bypasses emitter for AC                   │
│  R13 (56 Ω): negative DC feedback → thermal stability  │
└────────────────────┬────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────┐
│  STAGE 3 – BC639 pre-driver + BD139/BD140 push-pull     │
│  Class AB biased via VR3 (100 Ω) + D1 (1N4148)         │
│  C4 (220 µF) bootstrap → larger output swing            │
│  BD139 (NPN) sources; BD140 (PNP) sinks                │
└────────────────────┬────────────────────────────────────┘
                     │
                  [C_out 2200 µF]
                     │
                  [8 Ω Speaker]
```

**Power supply:** 18 V DC (full-wave rectifier not modelled in sim). ZD1 (10 V Zener) + R6 (330 Ω) provide a regulated 10 V rail for the pre-amp stages.

---

## Repository Structure

```
everyday-audio-enhancer/
├── simulation/
│   ├── audio_amplifier.cir   # LTspice-compatible SPICE netlist
│   └── analyze.py            # Python: plots freq response + transient
├── pcb/
│   └── component_placement.md  # PCB assembly notes + polarity guide
├── docs/
│   ├── circuit_diagram.png   # Circuit diagram (from report)
│   └── block_diagram.png     # System block diagram
└── README.md
```

---

## Getting Started

### SPICE Simulation

**LTspice** (free, recommended):
1. Open `simulation/audio_amplifier.cir` in LTspice
2. Run `.op` for DC bias, `.ac` for frequency response, `.tran` for transient
3. Probe `V(SPKR)` for output

**Python analysis** (theoretical curves if no SPICE raw file):
```bash
pip install numpy matplotlib scipy
python simulation/analyze.py

# If you have an LTspice .raw export:
python simulation/analyze.py --ltspice-raw simulation/audio_amplifier.raw
```

---

## Bill of Materials

| # | Component | Value | Function |
|---|---|---|---|
| 1 | Resistor R1 | 68 kΩ | JFET drain load |
| 2 | Resistor R2 | 1.8 kΩ | JFET source degeneration |
| 3 | Resistor R3 | 10 kΩ | BC548 bias |
| 4 | Resistor R5 | 6.8 kΩ | BC548 collector load |
| 5 | Resistor R6 | 330 Ω | Zener current limiter |
| 6 | Resistor R7/R8 | 180 Ω ×2 | Bootstrap bias divider |
| 7 | Resistor R9 | 33 Ω | Base stopper (T3→T4) |
| 8 | Resistor R13 | 56 Ω | Negative DC feedback |
| 9 | Resistor R_out | 6.8 Ω | Output series resistor |
| 10 | Resistor R_emitter | 2.2 Ω ×2 | Emitter ballast (T4, T5) |
| 11 | Resistor R_e | 3.9 Ω | Emitter resistor (T3) |
| 12 | VR1 | 1 MΩ log | Volume control |
| 13 | VR2 | 10 kΩ | Quiescent point (set to VCC/2) |
| 14 | VR3 | 100 Ω | Class AB bias current |
| 15 | C1 | 0.1 µF | Input coupling |
| 16 | C2 | 2.2 µF | Inter-stage coupling |
| 17 | C4 | 220 µF | Bootstrap capacitor |
| 18 | C8 | 470 µF | Emitter AC bypass |
| 19 | C_out | 2200 µF | Output coupling |
| 20 | C_supply | 100 µF | Supply decoupling |
| 21 | C_HF | 10 nF | HF stability |
| 22 | C_trim | 5 nF | HF compensation |
| 23 | ZD1 | 10 V Zener | Pre-amp rail regulation |
| 24 | D1 | 1N4148 | Class AB thermal tracking |
| 25 | T1 | 2N5484 | JFET input stage |
| 26 | T2 | BC548 | NPN voltage amplifier |
| 27 | T3 | BC639 | NPN pre-driver |
| 28 | T4 | BD139 | NPN output (positive half) |
| 29 | T5 | BD140 | PNP output (negative half) |
| 30 | Speaker | 8 Ω / 1.5 W | Load |

---

## PCB Assembly Notes

1. **Polarity-sensitive parts** — install diodes (ZD1, D1) and electrolytic capacitors (all polarised caps) with correct polarity before transistors
2. **BD139 / BD140 orientation** — the metallised (flat metal) face of both output transistors must face the **centre of the board** to allow heat spreading; add heatsink compound if driving near rated power
3. **Setting VR2** — after power-up with no audio input, adjust VR2 until the emitter voltage of T4/T5 reads VCC/2 (≈ 9 V for an 18 V supply)
4. **Setting VR3** — adjust while monitoring collector current of T4; set to ~20–40 mA quiescent for Class AB (crossover distortion vs. idle dissipation trade-off)
5. **VR1 taper** — must be **logarithmic (Type C)** for a natural-feeling volume sweep; a linear pot gives poor control at low volumes

---

## Theory of Operation

### Stage 1 – JFET Input (2N5484)
The 2N5484 N-channel JFET provides a very high input impedance (~1 MΩ, set by VR1) so the source signal is not loaded. Operating in common-source mode, it provides moderate voltage gain and feeds into the BC548 stage.

### Stage 2 – BC548 Voltage Amplifier
The main voltage gain occurs here. Resistor R13 (56 Ω) connects the output back to the emitter of T2, providing negative DC feedback that stabilises the operating point against temperature drift. Capacitor C8 (470 µF) ensures this feedback is DC-only, so AC gain is not reduced.

### Stage 3 – Class AB Push-Pull (BD139 + BD140)
The push-pull configuration uses NPN (BD139) for positive half-cycles and PNP (BD140) for negative half-cycles. VR3 + D1 set a small forward bias across the output transistors, eliminating crossover distortion without running them in pure Class A (which would waste power as heat). The bootstrap capacitor C4 improves the positive output voltage swing close to the supply rail.

### Negative Feedback and Stability
R13 closes a global feedback loop. When output voltage rises (e.g. temperature increase driving T4/T5 harder), the emitter voltage of T2 rises, reducing its transconductance and pulling the collector voltage up — which in turn reduces base drive to T3/T4/T5. This servo action keeps the quiescent point stable.

---

## Observations

| Signal point | Value |
|---|---|
| Input (AC, 1 kHz) | 100 mV peak |
| Output across speaker | 240 mV peak |
| Voltage gain | 2.4× (7.6 dB) |

The output waveform observed on the oscilloscope is a clean replica of the input sine wave with no visible crossover notch, confirming successful Class AB biasing.

---

## References

1. Jingjie Sun & Yingjun Chen — *Audio Amplifier Design*, University of Gävle, June 2011
2. Jun Honda & Jonathan Adams — *Class D Audio Amplifier Design*, International Rectifier
3. Raj K Gorkhali — *Electronics for You*, June 2020
4. Texas Instruments — Amplifier application notes (June 2021)
5. Electronics Tutorials — [electronicsurorials.ws](https://www.electronics-tutorials.ws)
6. Watelectronics — October 2019

---

## License

MIT License — see `LICENSE` for details.
