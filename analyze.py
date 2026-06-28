#!/usr/bin/env python3
"""
Everyday Audio Enhancer – Post-simulation analysis
===================================================
Reads LTspice raw output (or generates theoretical curves) and plots:
  1. Frequency response (Bode plot, 20 Hz – 20 kHz)
  2. Transient waveform comparison (input vs output)
  3. Component operating-point summary table

Requirements: pip install numpy matplotlib scipy ltspice (optional)
Run:  python simulation/analyze.py
      python simulation/analyze.py --ltspice-raw simulation/audio_amplifier.raw
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from pathlib import Path

# ── Circuit parameters (from report + BOM) ──────────────────────
VCC         = 18.0      # V supply
VCC_REG     = 10.0      # V after ZD1 regulator
R_LOAD      = 8.0       # Ω speaker
R_FEEDBACK  = 56.0      # R13 negative feedback
C_OUTPUT    = 2200e-6   # F output coupling cap
R_OUT       = 6.8       # Ω output resistor

# Measured / expected values from report
V_IN_MEAS   = 0.100     # V (100 mV)
V_OUT_MEAS  = 0.240     # V (240 mV)
GAIN_MEAS   = V_OUT_MEAS / V_IN_MEAS  # ≈ 2.4 → ~7.6 dB


def theoretical_frequency_response(freqs):
    """
    First-order high-pass (output coupling cap + speaker load) combined with
    first-order low-pass (transistor bandwidth).
    This is a simplified model for illustration; use SPICE .ac for accuracy.
    """
    # High-pass: fc_hp = 1 / (2π R_load C_out)  ≈ 9 Hz
    fc_hp = 1.0 / (2 * np.pi * (R_LOAD + R_OUT) * C_OUTPUT)
    # Low-pass: BJT bandwidth ~ 150 kHz for BD139 at this bias
    fc_lp = 150e3
    omega  = 2 * np.pi * freqs
    H_hp   = (1j * omega / (2 * np.pi * fc_hp)) / (1 + 1j * omega / (2 * np.pi * fc_hp))
    H_lp   = 1 / (1 + 1j * omega / (2 * np.pi * fc_lp))
    return GAIN_MEAS * np.abs(H_hp * H_lp)


def load_ltspice_raw(path: str):
    """Parse LTspice binary .raw file if ltspice library available."""
    try:
        import ltspice
        lts = ltspice.Ltspice(path)
        lts.parse()
        freq = lts.get_frequency()
        vout = np.abs(lts.get_data('V(SPKR)'))
        vin  = np.abs(lts.get_data('V(IN)'))
        return freq, 20 * np.log10(vout / vin)
    except Exception as e:
        print(f"[WARN] Could not parse LTspice raw: {e}. Using theoretical model.")
        return None, None


def plot_frequency_response(ax, freq, gain_db, theoretical=True):
    ax.semilogx(freq, gain_db, color='#2980b9', linewidth=2,
                label='Theoretical model' if theoretical else 'LTspice simulation')
    ax.axhline(y=max(gain_db) - 3, color='#e74c3c', linestyle='--', alpha=0.7,
               label='−3 dB reference')
    ax.axvline(x=20,    color='gray', linestyle=':', alpha=0.5, label='20 Hz / 20 kHz')
    ax.axvline(x=20000, color='gray', linestyle=':', alpha=0.5)
    ax.axhspan(max(gain_db) - 1, max(gain_db) + 1, alpha=0.1, color='green',
               label='±1 dB passband')
    ax.scatter([1000], [20 * np.log10(GAIN_MEAS)],
               color='#e67e22', zorder=5, s=80,
               label=f'Measured @ 1 kHz ({20*np.log10(GAIN_MEAS):.1f} dB)')
    ax.set_xlabel('Frequency (Hz)', fontsize=11)
    ax.set_ylabel('Gain (dB)', fontsize=11)
    ax.set_title('Frequency Response – Everyday Audio Enhancer', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, which='both', alpha=0.3)
    ax.set_xlim([10, 100e3])


def plot_transient(ax):
    """Simulated 1 kHz sine wave with measured gain."""
    t     = np.linspace(0, 3e-3, 3000)
    v_in  = V_IN_MEAS * np.sin(2 * np.pi * 1000 * t)
    # Simple gain + slight phase shift (typical of capacitively coupled stages)
    v_out = V_OUT_MEAS * np.sin(2 * np.pi * 1000 * t - np.deg2rad(12))
    ax.plot(t * 1e3, v_in  * 1e3, color='#2980b9', linewidth=1.5, label='Input (100 mV pk)')
    ax.plot(t * 1e3, v_out * 1e3, color='#e74c3c', linewidth=1.5, label='Output (240 mV pk)')
    ax.set_xlabel('Time (ms)', fontsize=11)
    ax.set_ylabel('Voltage (mV)', fontsize=11)
    ax.set_title('Transient Response @ 1 kHz (measured values)', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)


def print_operating_point():
    """Estimated DC operating points based on circuit topology."""
    print("\n── Estimated DC Operating Points ─────────────────────────")
    print(f"  Supply (VCC)            : {VCC:.1f} V")
    print(f"  Regulated pre-amp rail  : {VCC_REG:.1f} V  (via ZD1 + R6)")
    vout_dc = VCC / 2
    print(f"  Output quiescent (ideal): {vout_dc:.1f} V  (set by VR2)")
    print(f"  Gain measured @ 1 kHz   : {GAIN_MEAS:.2f}×  ({20*np.log10(GAIN_MEAS):.1f} dB)")
    print(f"  Vin                     : {V_IN_MEAS*1e3:.0f} mV")
    print(f"  Vout                    : {V_OUT_MEAS*1e3:.0f} mV")
    print(f"  Speaker load            : {R_LOAD:.0f} Ω")
    fc_hp = 1.0 / (2 * np.pi * (R_LOAD + R_OUT) * C_OUTPUT)
    print(f"  Low freq −3 dB (theory) : {fc_hp:.1f} Hz")
    print("──────────────────────────────────────────────────────────\n")


def main():
    parser = argparse.ArgumentParser(description='Audio amplifier analysis')
    parser.add_argument('--ltspice-raw', type=str, default=None,
                        help='Path to LTspice .raw file for AC analysis')
    parser.add_argument('--save', type=str, default='simulation/results.png',
                        help='Output image path')
    args = parser.parse_args()

    print_operating_point()

    # Frequency axis
    freqs = np.logspace(np.log10(10), np.log10(200e3), 2000)

    # Try real SPICE data, else use theory
    freq_spice, gain_spice = None, None
    if args.ltspice_raw:
        freq_spice, gain_spice = load_ltspice_raw(args.ltspice_raw)

    fig = plt.figure(figsize=(14, 8))
    fig.suptitle('Everyday Audio Enhancer – Analysis', fontsize=15, fontweight='bold', y=0.98)
    gs  = gridspec.GridSpec(1, 2, figure=fig, hspace=0.35, wspace=0.32)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])

    if freq_spice is not None:
        plot_frequency_response(ax1, freq_spice, gain_spice, theoretical=False)
    else:
        gain_theory = 20 * np.log10(theoretical_frequency_response(freqs))
        plot_frequency_response(ax1, freqs, gain_theory, theoretical=True)

    plot_transient(ax2)

    out_path = Path(args.save)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_path, dpi=150, bbox_inches='tight')
    print(f"[INFO] Plot saved to {out_path}")
    plt.show()


if __name__ == '__main__':
    main()
