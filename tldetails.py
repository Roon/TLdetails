#!/usr/bin/env python3
"""
TLDetails - Transmission Line Details Calculator
Python clone of the original Visual Basic program by Dan Maguire (AC6LA)
https://www.ac6la.com/tldetails1.html
"""

import math
import cmath
import sys
from typing import Optional

# Speed of light in m/s
C = 2.99792458e8

# Unit conversion
FT_PER_M = 3.28084
DB_PER_NP = 8.68589  # dB per Neper

# ---------------------------------------------------------------------------
# Cable database
# Zo = nominal characteristic impedance (ohms)
# VF = velocity factor (0..1)
# K0, K1, K2 = loss coefficients: MLL(dB/100ft) = K0 + K1*sqrt(f_MHz) + K2*f_MHz
# ---------------------------------------------------------------------------
CABLES = {
    # --- 50-ohm coax ---
    "RG-58C/U":          {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.10121, "K2": 0.003993},
    "RG-58A/U":          {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.10121, "K2": 0.003993},
    "Belden 8262":       {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.10121, "K2": 0.003993},
    "RG-8X":             {"Zo": 50.0, "VF": 0.820, "K0": 0.0, "K1": 0.07490, "K2": 0.002204},
    "Belden 9258":       {"Zo": 50.0, "VF": 0.820, "K0": 0.0, "K1": 0.07490, "K2": 0.002204},
    "RG-8/U":            {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.04898, "K2": 0.001515},
    "Belden 8237":       {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.04898, "K2": 0.001515},
    "RG-213/U":          {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.05085, "K2": 0.002806},
    "Belden 8267":       {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.05085, "K2": 0.002806},
    "RG-214":            {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.04898, "K2": 0.001515},
    "RG-217":            {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.03710, "K2": 0.001160},
    "RG-218":            {"Zo": 50.0, "VF": 0.659, "K0": 0.0, "K1": 0.02640, "K2": 0.000780},
    "RG-174":            {"Zo": 50.0, "VF": 0.660, "K0": 0.0, "K1": 0.17750, "K2": 0.006670},
    "RG-316":            {"Zo": 50.0, "VF": 0.695, "K0": 0.0, "K1": 0.14370, "K2": 0.003380},
    "RG-142":            {"Zo": 50.0, "VF": 0.695, "K0": 0.0, "K1": 0.09160, "K2": 0.002030},
    "RG-393":            {"Zo": 50.0, "VF": 0.695, "K0": 0.0, "K1": 0.05100, "K2": 0.001370},
    "LMR-195":           {"Zo": 50.0, "VF": 0.800, "K0": 0.0, "K1": 0.04880, "K2": 0.001370},
    "LMR-240":           {"Zo": 50.0, "VF": 0.840, "K0": 0.0, "K1": 0.03645, "K2": 0.000825},
    "LMR-300":           {"Zo": 50.0, "VF": 0.850, "K0": 0.0, "K1": 0.02780, "K2": 0.000610},
    "LMR-400":           {"Zo": 50.0, "VF": 0.850, "K0": 0.0, "K1": 0.02179, "K2": 0.000330},
    "LMR-500":           {"Zo": 50.0, "VF": 0.860, "K0": 0.0, "K1": 0.01720, "K2": 0.000270},
    "LMR-600":           {"Zo": 50.0, "VF": 0.870, "K0": 0.0, "K1": 0.01447, "K2": 0.000148},
    "Belden 9913":       {"Zo": 50.0, "VF": 0.840, "K0": 0.0, "K1": 0.02943, "K2": 0.000691},
    "Belden 7810A":      {"Zo": 50.0, "VF": 0.780, "K0": 0.0, "K1": 0.06880, "K2": 0.001910},
    "Heliax FSJ1-50A":   {"Zo": 50.0, "VF": 0.840, "K0": 0.0, "K1": 0.04450, "K2": 0.000760},
    "Heliax FSJ2-50":    {"Zo": 50.0, "VF": 0.830, "K0": 0.0, "K1": 0.02770, "K2": 0.000420},
    "Heliax FSJ4-50B":   {"Zo": 50.0, "VF": 0.810, "K0": 0.0, "K1": 0.01780, "K2": 0.000260},
    "Heliax LDF4-50A":   {"Zo": 50.0, "VF": 0.880, "K0": 0.0, "K1": 0.01040, "K2": 0.000150},
    "Heliax LDF5-50A":   {"Zo": 50.0, "VF": 0.890, "K0": 0.0, "K1": 0.00643, "K2": 0.000093},
    "Heliax LDF6-50":    {"Zo": 50.0, "VF": 0.890, "K0": 0.0, "K1": 0.00440, "K2": 0.000066},
    "1/2in Hardline 50": {"Zo": 50.0, "VF": 0.870, "K0": 0.0, "K1": 0.01060, "K2": 0.000175},
    "7/8in Hardline 50": {"Zo": 50.0, "VF": 0.880, "K0": 0.0, "K1": 0.00570, "K2": 0.000087},
    "1-5/8in Hardline 50":{"Zo":50.0, "VF": 0.880, "K0": 0.0, "K1": 0.00285, "K2": 0.000046},
    # --- 75-ohm coax ---
    "RG-59/U":           {"Zo": 75.0, "VF": 0.659, "K0": 0.0, "K1": 0.10040, "K2": 0.003600},
    "Belden 8241":       {"Zo": 75.0, "VF": 0.659, "K0": 0.0, "K1": 0.10040, "K2": 0.003600},
    "RG-6/U":            {"Zo": 75.0, "VF": 0.820, "K0": 0.0, "K1": 0.05452, "K2": 0.000720},
    "RG-11/U":           {"Zo": 75.0, "VF": 0.660, "K0": 0.0, "K1": 0.03966, "K2": 0.001300},
    "Belden 1694A":      {"Zo": 75.0, "VF": 0.820, "K0": 0.0, "K1": 0.03510, "K2": 0.000384},
    # --- Open wire / balanced ---
    "300-ohm Twinlead":  {"Zo": 300.0, "VF": 0.800, "K0": 0.0, "K1": 0.01800, "K2": 0.001600},
    "450-ohm Ladder":    {"Zo": 450.0, "VF": 0.910, "K0": 0.0, "K1": 0.00550, "K2": 0.000060},
    "600-ohm Open Wire": {"Zo": 600.0, "VF": 0.975, "K0": 0.0, "K1": 0.00280, "K2": 0.000030},
    # --- Custom (user-editable) ---
    "Custom":            {"Zo": 50.0, "VF": 0.800, "K0": 0.0, "K1": 0.05000, "K2": 0.001000},
}


# ---------------------------------------------------------------------------
# Core transmission line math
# ---------------------------------------------------------------------------

def matched_line_loss_db(f_MHz: float, K0: float, K1: float, K2: float) -> float:
    """Matched line loss in dB/100ft at frequency f_MHz."""
    f = max(f_MHz, 1e-9)
    return K0 + K1 * math.sqrt(f) + K2 * f


def _alpha_np_per_m(f_MHz: float, K0: float, K1: float, K2: float) -> float:
    """Attenuation constant in Np/m from K-coefficient loss model."""
    mll = matched_line_loss_db(f_MHz, K0, K1, K2)  # dB/100ft
    return mll / (100.0 / FT_PER_M * DB_PER_NP)


def _beta_rad_per_m(f_MHz: float, VF: float) -> float:
    """Phase constant in rad/m."""
    return 2.0 * math.pi * f_MHz * 1e6 / (VF * C)


def propagation_constant(f_MHz: float, cable: dict) -> complex:
    """γ = α + jβ  (Np/m, rad/m)."""
    a = _alpha_np_per_m(f_MHz, cable["K0"], cable["K1"], cable["K2"])
    b = _beta_rad_per_m(f_MHz, cable["VF"])
    return complex(a, b)


def characteristic_impedance(f_MHz: float, cable: dict) -> complex:
    """
    Frequency-dependent complex Zo derived from RLGC.

    At high frequency this approaches the nominal (real) Zo.
    At low frequency skin-effect and dielectric terms shift the phase.
    """
    Zo0 = cable["Zo"]
    VF  = cable["VF"]
    f   = max(f_MHz, 1e-6)
    omega = 2.0 * math.pi * f * 1e6

    # L and C from high-frequency (lossless) Zo and VF
    L   = Zo0 / (VF * C)          # H/m
    Cap = 1.0 / (Zo0 * VF * C)    # F/m

    # R from K0 (DC) + K1 (skin effect) terms: alpha_R = R / (2*Zo0)
    alpha_r = (cable["K0"] + cable["K1"] * math.sqrt(f)) / (100.0 / FT_PER_M * DB_PER_NP)
    R = 2.0 * Zo0 * alpha_r        # Ω/m

    # G from K2 (dielectric) term: alpha_G = G*Zo0 / 2
    alpha_g = cable["K2"] * f / (100.0 / FT_PER_M * DB_PER_NP)
    G = 2.0 * alpha_g / Zo0        # S/m

    Zs = complex(R, omega * L)
    Yp = complex(G, omega * Cap)
    return cmath.sqrt(Zs / Yp)


def rlgc_params(f_MHz: float, cable: dict) -> dict:
    """Return R, L, G, C per metre at frequency f_MHz."""
    Zo0 = cable["Zo"]
    VF  = cable["VF"]
    f   = max(f_MHz, 1e-6)
    omega = 2.0 * math.pi * f * 1e6

    L   = Zo0 / (VF * C)
    Cap = 1.0 / (Zo0 * VF * C)

    alpha_r = (cable["K0"] + cable["K1"] * math.sqrt(f)) / (100.0 / FT_PER_M * DB_PER_NP)
    R = 2.0 * Zo0 * alpha_r

    alpha_g = cable["K2"] * f / (100.0 / FT_PER_M * DB_PER_NP)
    G = 2.0 * alpha_g / Zo0

    return {"R": R, "L": L, "G": G, "C": Cap}


def input_impedance(ZL: complex, Zo: complex, gamma: complex, length_m: float) -> complex:
    """Zin of a terminated transmission line."""
    gl = gamma * length_m
    tanh_gl = cmath.tanh(gl)
    return Zo * (ZL + Zo * tanh_gl) / (Zo + ZL * tanh_gl)


def reflection_coeff(Z: complex, Zo_ref: complex) -> complex:
    return (Z - Zo_ref) / (Z + Zo_ref)


def swr_from_gamma(Gamma: complex) -> float:
    rho = abs(Gamma)
    if rho >= 1.0:
        return float("inf")
    return (1.0 + rho) / (1.0 - rho)


def return_loss_db(Gamma: complex) -> float:
    rho = abs(Gamma)
    if rho <= 0.0:
        return float("inf")
    return -20.0 * math.log10(rho)


# ---------------------------------------------------------------------------
# Single-frequency analysis
# ---------------------------------------------------------------------------

def analyze(cable: dict, f_MHz: float, ZL: complex, length_ft: float,
            Zo_override: Optional[float] = None,
            VF_override: Optional[float] = None) -> dict:
    """Full single-frequency transmission line analysis."""
    if Zo_override is not None or VF_override is not None:
        cable = dict(cable)
        if Zo_override is not None:
            cable["Zo"] = float(Zo_override)
        if VF_override is not None:
            cable["VF"] = float(VF_override)

    length_m = length_ft / FT_PER_M
    Zo0 = cable["Zo"]

    g    = propagation_constant(f_MHz, cable)
    Zo_c = characteristic_impedance(f_MHz, cable)
    rlgc = rlgc_params(f_MHz, cable)

    # Load end
    Gamma_L = reflection_coeff(ZL, Zo_c)
    SWR_L   = swr_from_gamma(Gamma_L)
    RL_L    = return_loss_db(Gamma_L)

    # Source end
    Zin     = input_impedance(ZL, Zo_c, g, length_m)
    Gamma_in = reflection_coeff(Zin, complex(Zo0, 0))
    SWR_in  = swr_from_gamma(Gamma_in)
    RL_in   = return_loss_db(Gamma_in)

    # Loss
    mll_per_100ft = matched_line_loss_db(f_MHz, cable["K0"], cable["K1"], cable["K2"])
    mll_total     = mll_per_100ft * length_ft / 100.0

    # Additional loss from mismatch (Sabin / ARRL formula)
    rho_L     = abs(Gamma_L)
    exp2al    = math.exp(-2.0 * g.real * length_m)
    if rho_L > 0.0 and exp2al < 1.0:
        denom = (1.0 - rho_L**2 * exp2al)
        if denom > 0.0:
            add_loss = -10.0 * math.log10(
                exp2al * (1.0 - rho_L**2) / denom
            ) - mll_total
            add_loss = max(0.0, add_loss)
        else:
            add_loss = 0.0
    else:
        add_loss = 0.0

    # One-way delay
    delay_ns = (length_m / (cable["VF"] * C)) * 1e9

    return {
        "f_MHz":            f_MHz,
        "cable":            cable,
        "Zo_complex":       Zo_c,
        "gamma":            g,
        "rlgc":             rlgc,
        "length_ft":        length_ft,
        "length_m":         length_m,
        "delay_ns":         delay_ns,
        "mll_per_100ft":    mll_per_100ft,
        "mll_total_dB":     mll_total,
        "additional_loss_dB": add_loss,
        "total_loss_dB":    mll_total + add_loss,
        "ZL":               ZL,
        "Gamma_L":          Gamma_L,
        "SWR_L":            SWR_L,
        "RL_L_dB":          RL_L,
        "Zin":              Zin,
        "Gamma_in":         Gamma_in,
        "SWR_in":           SWR_in,
        "RL_in_dB":         RL_in,
    }


# ---------------------------------------------------------------------------
# Formatted output
# ---------------------------------------------------------------------------

def _fmt_z(z: complex) -> str:
    sign = "+" if z.imag >= 0 else "-"
    return f"{z.real:.4f} {sign} {abs(z.imag):.4f}j Ω"


def print_analysis(r: dict, cable_name: str = ""):
    c = r["cable"]
    g = r["gamma"]
    rl = r["rlgc"]
    sep = "=" * 62

    print(f"\n{sep}")
    print(f"  TLDetails Analysis")
    print(sep)
    if cable_name:
        print(f"  Cable       : {cable_name}")
    print(f"  Zo (nom.)   : {c['Zo']:.1f} Ω    VF: {c['VF']:.4f}")
    print(f"  K0={c['K0']:.5f}  K1={c['K1']:.5f}  K2={c['K2']:.6f}")
    print(f"  Frequency   : {r['f_MHz']:.4f} MHz")
    print(f"  Length      : {r['length_ft']:.4f} ft  ({r['length_m']:.4f} m)")
    print()

    Zo_c = r["Zo_complex"]
    print(f"  Zo (complex): {_fmt_z(Zo_c)}")
    print(f"  γ           : {g.real:.6f} + {g.imag:.6f}j  (Np/m, rad/m)")
    print()

    print(f"  --- RLGC Parameters (per metre) ---")
    print(f"  R = {rl['R']:.6f}  Ω/m     L = {rl['L']*1e6:.6f}  µH/m")
    print(f"  G = {rl['G']*1e6:.6f} µS/m     C = {rl['C']*1e12:.6f}  pF/m")
    print(f"  One-way delay: {r['delay_ns']:.4f} ns")
    print()

    ZL = r["ZL"]
    GL = r["Gamma_L"]
    print(f"  --- Load End (Port 2) ---")
    print(f"  ZL          : {_fmt_z(ZL)}")
    print(f"  Rho         : {abs(GL):.5f}  ∠{math.degrees(cmath.phase(GL)):.2f}°")
    print(f"  SWR         : {r['SWR_L']:.4f}")
    print(f"  Return Loss : {r['RL_L_dB']:.4f} dB")
    print()

    Zin = r["Zin"]
    Gin = r["Gamma_in"]
    print(f"  --- Source End (Port 1) ---")
    print(f"  Zin         : {_fmt_z(Zin)}")
    print(f"  Rho         : {abs(Gin):.5f}  ∠{math.degrees(cmath.phase(Gin)):.2f}°")
    print(f"  SWR         : {r['SWR_in']:.4f}")
    print(f"  Return Loss : {r['RL_in_dB']:.4f} dB")
    print()

    print(f"  --- Power Loss ---")
    print(f"  Matched Line Loss : {r['mll_per_100ft']:.4f} dB/100ft  "
          f"({r['mll_total_dB']:.4f} dB total)")
    print(f"  Additional (SWR)  : {r['additional_loss_dB']:.4f} dB")
    print(f"  Total Loss        : {r['total_loss_dB']:.4f} dB")
    print(sep)


# ---------------------------------------------------------------------------
# Frequency sweep + plotting
# ---------------------------------------------------------------------------

def sweep(cable: dict, f_start: float, f_stop: float, ZL: complex,
          length_ft: float, n: int = 300) -> dict:
    """Compute arrays of results across a frequency range."""
    import numpy as np
    freqs = np.linspace(max(f_start, 0.001), f_stop, n)

    keys = ["mll_per_100ft", "SWR_in", "SWR_L", "RL_in_dB", "RL_L_dB",
            "total_loss_dB", "delay_ns"]
    data = {k: [] for k in keys}
    data["Zo_mag"] = []
    data["VF_eff"] = []
    data["freqs"]  = freqs

    for f in freqs:
        r = analyze(cable, float(f), ZL, length_ft)
        for k in keys:
            data[k].append(r[k])
        data["Zo_mag"].append(abs(r["Zo_complex"]))
        beta = r["gamma"].imag
        vf_eff = (2.0 * math.pi * f * 1e6 / (beta * C)) if beta > 0 else cable["VF"]
        data["VF_eff"].append(vf_eff)

    return data


def plot_sweep(cable: dict, cable_name: str, f_start: float, f_stop: float,
               ZL: complex, length_ft: float):
    try:
        import matplotlib.pyplot as plt
        import numpy as np
    except ImportError:
        print("matplotlib not installed — cannot plot. Run: pip install matplotlib")
        return

    d = sweep(cable, f_start, f_stop, ZL, length_ft)
    fs = d["freqs"]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(
        f"TLDetails: {cable_name}   {length_ft:.0f} ft   "
        f"ZL = {ZL.real:.1f}{ZL.imag:+.1f}j Ω",
        fontsize=12
    )

    ax = axes[0, 0]
    ax.plot(fs, d["mll_per_100ft"], "b-")
    ax.set_title("Matched Line Loss (dB/100ft)")
    ax.set_xlabel("MHz"); ax.grid(True)

    ax = axes[0, 1]
    ax.plot(fs, d["Zo_mag"], "r-")
    ax.set_title("|Zo| (Ω)")
    ax.set_xlabel("MHz"); ax.grid(True)

    ax = axes[1, 0]
    ax.plot(fs, d["VF_eff"], "g-")
    ax.set_title("Velocity Factor")
    ax.set_xlabel("MHz"); ax.grid(True)

    ax = axes[1, 1]
    swr_in = np.clip(d["SWR_in"], 0, 50)
    swr_l  = np.clip(d["SWR_L"],  0, 50)
    ax.plot(fs, swr_in, "b-", label="Source end")
    ax.plot(fs, swr_l,  "r--", label="Load end")
    ax.set_title("SWR")
    ax.set_xlabel("MHz"); ax.legend(); ax.grid(True)

    plt.tight_layout()
    plt.show()


# ---------------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------------

def _prompt_float(msg: str, default: Optional[float] = None) -> float:
    suffix = f" [{default}]" if default is not None else ""
    while True:
        raw = input(f"  {msg}{suffix}: ").strip()
        if raw == "" and default is not None:
            return float(default)
        try:
            return float(raw)
        except ValueError:
            print("  (enter a number)")


def interactive():
    print("\nTLDetails — Transmission Line Details Calculator (Python)")
    print("  Clone of AC6LA's TLDetails  |  https://www.ac6la.com/tldetails1.html\n")

    cable_names = sorted(CABLES.keys())

    while True:
        print("\nAvailable cables:")
        for i, name in enumerate(cable_names, 1):
            c = CABLES[name]
            print(f"  {i:3d}. {name:<26} Zo={c['Zo']:5.1f}Ω  VF={c['VF']:.3f}")

        raw = input("\nSelect cable number (or 0 to quit): ").strip()
        if raw == "0" or raw.lower() in ("q", "quit", "exit"):
            break
        try:
            idx = int(raw) - 1
        except ValueError:
            print("  Enter a number."); continue
        if not (0 <= idx < len(cable_names)):
            print("  Out of range."); continue

        cable_name = cable_names[idx]
        cable = dict(CABLES[cable_name])

        # Allow overrides
        print(f"\n  Selected: {cable_name}  Zo={cable['Zo']}Ω  VF={cable['VF']}")
        ov = input("  Override Zo or VF? (y/n) [n]: ").strip().lower()
        if ov == "y":
            cable["Zo"] = _prompt_float("Zo (Ω)", cable["Zo"])
            cable["VF"] = _prompt_float("VF",     cable["VF"])

        length_ft = _prompt_float("Line length (ft)")
        f_MHz     = _prompt_float("Frequency (MHz)")
        ZL_r      = _prompt_float("Load resistance (Ω)", 50.0)
        ZL_i      = _prompt_float("Load reactance  (Ω)", 0.0)
        ZL        = complex(ZL_r, ZL_i)

        result = analyze(cable, f_MHz, ZL, length_ft)
        print_analysis(result, cable_name)

        sweep_yn = input("\n  Frequency sweep / plot? (y/n) [n]: ").strip().lower()
        if sweep_yn == "y":
            f_start = _prompt_float("Start freq (MHz)", 1.0)
            f_stop  = _prompt_float("Stop freq  (MHz)", 30.0)
            plot_sweep(cable, cable_name, f_start, f_stop, ZL, length_ft)


# ---------------------------------------------------------------------------
# Smith chart drawing
# ---------------------------------------------------------------------------

def _draw_smith_grid(ax, Zo: float = 50.0):
    """Draw a normalised Smith chart grid on a matplotlib Axes."""
    import numpy as np

    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.axhline(0, color="k", linewidth=0.8)

    theta = np.linspace(0, 2 * np.pi, 800)

    # Outer unit circle
    ax.plot(np.cos(theta), np.sin(theta), "k-", linewidth=1.5)

    # Constant-resistance circles: r/(1+r) centre, 1/(1+r) radius
    for r in (0, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0):
        cx  = r / (1.0 + r)
        rad = 1.0 / (1.0 + r)
        circle = plt.Circle((cx, 0), rad, fill=False, color="#888888", linewidth=0.6)
        ax.add_patch(circle)
        lx = cx - rad
        if abs(lx) <= 1.0:
            ax.text(lx, 0.03, f"{r:g}", fontsize=6, color="#666666", ha="center")

    # Constant-reactance arcs: centre (1, 1/x), radius 1/|x|
    t = np.linspace(0, 2 * np.pi, 2000)
    for x in (0.2, 0.5, 1.0, 2.0, 5.0):
        for sign in (1, -1):
            rad = 1.0 / x
            px  = 1.0 + rad * np.cos(t)
            py  = sign / x + rad * np.sin(t)
            mask = px ** 2 + py ** 2 <= 1.0005
            # split into contiguous segments and plot each
            segs, cur = [], []
            for xi, yi, m in zip(px, py, mask):
                if m:
                    cur.append((xi, yi))
                elif cur:
                    segs.append(cur); cur = []
            if cur:
                segs.append(cur)
            for seg in segs:
                sx, sy = zip(*seg)
                ax.plot(sx, sy, color="#888888", linewidth=0.6)
            # label near the rim
            label_y = sign * 0.90 / x
            if abs(label_y) <= 1.05:
                ax.text(0.97, label_y, f"j{sign*x:g}", fontsize=6,
                        color="#666666", ha="center")

    # SWR reference circles (dashed, light blue)
    for swr_val in (1.5, 2.0, 3.0, 5.0):
        rho = (swr_val - 1.0) / (swr_val + 1.0)
        circle = plt.Circle((0, 0), rho, fill=False,
                             color="#aaddff", linewidth=0.7, linestyle="--")
        ax.add_patch(circle)
        ax.text(0, rho + 0.03, f"SWR {swr_val:g}", fontsize=5,
                color="#88aacc", ha="center")


# ---------------------------------------------------------------------------
# Tkinter GUI
# ---------------------------------------------------------------------------

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    _GUI_AVAILABLE = True
except Exception:
    _GUI_AVAILABLE = False


class TLDetailsGUI:
    """Main application window."""

    _PAD = {"padx": 6, "pady": 4}

    def __init__(self, root: "tk.Tk"):
        self.root = root
        self.root.title("TLDetails — Transmission Line Calculator")
        self.root.resizable(True, True)
        self.root.columnconfigure(0, weight=1)

        self._after_id  = None
        self._result    = None
        self._sweep_top = None
        self._smith_top = None
        self._cable_names = sorted(CABLES.keys())

        self._build()
        self._on_cable_change()

    # ------------------------------------------------------------------ build

    def _build(self):
        p = self._PAD

        # ── Cable row ──────────────────────────────────────────────────────
        cf = ttk.LabelFrame(self.root, text="Cable")
        cf.grid(row=0, column=0, sticky="ew", **p)
        cf.columnconfigure(1, weight=1)

        ttk.Label(cf, text="Type:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self._cable_var = tk.StringVar(value=self._cable_names[0])
        cb = ttk.Combobox(cf, textvariable=self._cable_var,
                          values=self._cable_names, width=28, state="readonly")
        cb.grid(row=0, column=1, sticky="ew", padx=4, pady=4)
        cb.bind("<<ComboboxSelected>>", self._on_cable_change)

        for col, (lbl, attr, w) in enumerate([
            ("Zo (Ω):", "_zo_var",  7),
            ("VF:",     "_vf_var",  7),
            ("K0:",     "_k0_var",  9),
            ("K1:",     "_k1_var",  9),
            ("K2:",     "_k2_var", 10),
        ], start=2):
            ttk.Label(cf, text=lbl).grid(row=0, column=col*2,   sticky="e", padx=(8, 2))
            var = tk.StringVar()
            setattr(self, attr, var)
            state = "normal" if attr in ("_zo_var", "_vf_var") else "readonly"
            e = ttk.Entry(cf, textvariable=var, width=w, state=state)
            e.grid(row=0, column=col*2+1, padx=(0, 4), pady=4)
            if state == "normal":
                e.bind("<FocusOut>", self._schedule_compute)
                e.bind("<Return>",   self._schedule_compute)

        # ── Middle row: Inputs | Line info ─────────────────────────────────
        mid = ttk.Frame(self.root)
        mid.grid(row=1, column=0, sticky="nsew", **p)
        mid.columnconfigure(0, weight=1)
        mid.columnconfigure(1, weight=1)

        inf = ttk.LabelFrame(mid, text="Inputs")
        inf.grid(row=0, column=0, sticky="nsew", padx=(0, 4))

        inputs = [
            ("Frequency (MHz):", "_freq_var",   "14.2000",  0.001, 100000, 1.0),
            ("Length (ft):",     "_length_var", "100.0000", 0.001,  1e6,  10.0),
            ("Load R (Ω):",      "_zlr_var",    "50.0000",  -9999,  9999,  1.0),
            ("Load X (Ω):",      "_zlx_var",    "0.0000",   -9999,  9999,  1.0),
        ]
        for row, (lbl, attr, default, lo, hi, inc) in enumerate(inputs):
            ttk.Label(inf, text=lbl).grid(row=row, column=0, sticky="w", padx=6, pady=4)
            var = tk.StringVar(value=default)
            setattr(self, attr, var)
            sb = ttk.Spinbox(inf, textvariable=var, from_=lo, to=hi,
                             increment=inc, width=14, format="%.4f")
            sb.grid(row=row, column=1, sticky="ew", padx=6, pady=4)
            var.trace_add("write", self._schedule_compute)

        lif = ttk.LabelFrame(mid, text="Line Parameters")
        lif.grid(row=0, column=1, sticky="nsew")
        lif.columnconfigure(1, weight=1)

        self._line_vars = {}
        for row, (key, lbl) in enumerate([
            ("zo_cpx",  "Zo (complex):"),
            ("gamma",   "γ (Np/m, rad/m):"),
            ("delay",   "One-way delay:"),
            ("mll100",  "MLL (dB/100ft):"),
        ]):
            ttk.Label(lif, text=lbl).grid(row=row, column=0, sticky="w", padx=6, pady=3)
            v = tk.StringVar(value="—")
            ttk.Label(lif, textvariable=v, width=28, anchor="w",
                      relief="sunken", background="#f0f0f0").grid(
                row=row, column=1, sticky="ew", padx=6, pady=3)
            self._line_vars[key] = v

        # ── Port frames ────────────────────────────────────────────────────
        ends = ttk.Frame(self.root)
        ends.grid(row=2, column=0, sticky="nsew", **p)
        ends.columnconfigure(0, weight=1)
        ends.columnconfigure(1, weight=1)

        self._port_vars = {}
        for col, (tag, title) in enumerate([
            ("load",   "Load End (Port 2)"),
            ("source", "Source End (Port 1)"),
        ]):
            pf = ttk.LabelFrame(ends, text=title)
            pf.grid(row=0, column=col, sticky="nsew",
                    padx=(0, 4) if col == 0 else (4, 0))
            pf.columnconfigure(1, weight=1)
            self._port_vars[tag] = {}
            for row, (key, lbl) in enumerate([
                ("Z",   "Z (Ω):"),
                ("rho", "Rho:"),
                ("ang", "Angle:"),
                ("swr", "SWR:"),
                ("rl",  "Return Loss:"),
            ]):
                ttk.Label(pf, text=lbl).grid(row=row, column=0, sticky="w", padx=6, pady=3)
                v = tk.StringVar(value="—")
                ttk.Label(pf, textvariable=v, width=24, anchor="w",
                          relief="sunken", background="#f0f0f0").grid(
                    row=row, column=1, sticky="ew", padx=6, pady=3)
                self._port_vars[tag][key] = v

        # ── Bottom row: Loss | RLGC ────────────────────────────────────────
        bot = ttk.Frame(self.root)
        bot.grid(row=3, column=0, sticky="nsew", **p)
        bot.columnconfigure(0, weight=1)
        bot.columnconfigure(1, weight=1)

        lossf = ttk.LabelFrame(bot, text="Power Loss")
        lossf.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
        lossf.columnconfigure(1, weight=1)

        self._loss_vars = {}
        for row, (key, lbl) in enumerate([
            ("mll_total",  "MLL total (dB):"),
            ("add_loss",   "Additional loss (dB):"),
            ("total_loss", "Total loss (dB):"),
        ]):
            ttk.Label(lossf, text=lbl).grid(row=row, column=0, sticky="w", padx=6, pady=3)
            v = tk.StringVar(value="—")
            ttk.Label(lossf, textvariable=v, width=16, anchor="w",
                      relief="sunken", background="#f0f0f0").grid(
                row=row, column=1, sticky="ew", padx=6, pady=3)
            self._loss_vars[key] = v

        rlgcf = ttk.LabelFrame(bot, text="RLGC  (per metre)")
        rlgcf.grid(row=0, column=1, sticky="nsew")
        rlgcf.columnconfigure(1, weight=1)

        self._rlgc_vars = {}
        for row, (key, lbl) in enumerate([
            ("R", "R (Ω/m):"),
            ("L", "L (µH/m):"),
            ("G", "G (µS/m):"),
            ("C", "C (pF/m):"),
        ]):
            ttk.Label(rlgcf, text=lbl).grid(row=row, column=0, sticky="w", padx=6, pady=3)
            v = tk.StringVar(value="—")
            ttk.Label(rlgcf, textvariable=v, width=16, anchor="w",
                      relief="sunken", background="#f0f0f0").grid(
                row=row, column=1, sticky="ew", padx=6, pady=3)
            self._rlgc_vars[key] = v

        # ── Buttons ────────────────────────────────────────────────────────
        bf = ttk.Frame(self.root)
        bf.grid(row=4, column=0, pady=8)

        ttk.Button(bf, text="Compute",     command=self._compute).pack(side="left", padx=8)
        ttk.Button(bf, text="Sweep Plot",  command=self._open_sweep).pack(side="left", padx=8)
        ttk.Button(bf, text="Smith Chart", command=self._open_smith).pack(side="left", padx=8)

    # ---------------------------------------------------------------- events

    def _on_cable_change(self, *_):
        name = self._cable_var.get()
        c = CABLES.get(name, CABLES["Custom"])
        self._zo_var.set(f"{c['Zo']:.1f}")
        self._vf_var.set(f"{c['VF']:.4f}")
        self._k0_var.set(f"{c['K0']:.5f}")
        self._k1_var.set(f"{c['K1']:.5f}")
        self._k2_var.set(f"{c['K2']:.6f}")
        self._schedule_compute()

    def _schedule_compute(self, *_):
        if self._after_id:
            self.root.after_cancel(self._after_id)
        self._after_id = self.root.after(350, self._compute)

    def _get_cable(self):
        name  = self._cable_var.get()
        cable = dict(CABLES.get(name, CABLES["Custom"]))
        cable["Zo"] = float(self._zo_var.get())
        cable["VF"] = float(self._vf_var.get())
        return cable

    def _get_inputs(self):
        cable     = self._get_cable()
        f_MHz     = float(self._freq_var.get())
        length_ft = float(self._length_var.get())
        ZL        = complex(float(self._zlr_var.get()), float(self._zlx_var.get()))
        return cable, f_MHz, length_ft, ZL

    def _compute(self, *_):
        self._after_id = None
        try:
            cable, f_MHz, length_ft, ZL = self._get_inputs()
        except (ValueError, tk.TclError):
            return

        try:
            r = analyze(cable, f_MHz, ZL, length_ft)
        except Exception as exc:
            messagebox.showerror("Calculation error", str(exc))
            return

        self._result = r
        g   = r["gamma"]
        Zo_c = r["Zo_complex"]
        rl  = r["rlgc"]

        def fz(z):
            s = "+" if z.imag >= 0 else "-"
            return f"{z.real:.4f} {s} {abs(z.imag):.4f}j Ω"

        self._line_vars["zo_cpx"].set(fz(Zo_c))
        self._line_vars["gamma"].set(f"{g.real:.6f} + {g.imag:.6f}j")
        self._line_vars["delay"].set(f"{r['delay_ns']:.4f} ns")
        self._line_vars["mll100"].set(f"{r['mll_per_100ft']:.4f} dB/100ft")

        for tag, (Z, Gamma, swr_val, rl_dB) in {
            "load":   (r["ZL"],  r["Gamma_L"], r["SWR_L"],  r["RL_L_dB"]),
            "source": (r["Zin"], r["Gamma_in"], r["SWR_in"], r["RL_in_dB"]),
        }.items():
            pv = self._port_vars[tag]
            pv["Z"].set(fz(Z))
            pv["rho"].set(f"{abs(Gamma):.5f}")
            pv["ang"].set(f"{math.degrees(cmath.phase(Gamma)):.2f}°")
            pv["swr"].set(f"{swr_val:.4f}")
            pv["rl"].set(f"{rl_dB:.4f} dB")

        self._loss_vars["mll_total"].set(f"{r['mll_total_dB']:.4f} dB")
        self._loss_vars["add_loss"].set(f"{r['additional_loss_dB']:.4f} dB")
        self._loss_vars["total_loss"].set(f"{r['total_loss_dB']:.4f} dB")

        self._rlgc_vars["R"].set(f"{rl['R']:.6f}")
        self._rlgc_vars["L"].set(f"{rl['L']*1e6:.6f}")
        self._rlgc_vars["G"].set(f"{rl['G']*1e6:.6f}")
        self._rlgc_vars["C"].set(f"{rl['C']*1e12:.6f}")

        # Refresh open child windows if present
        if self._smith_top and self._smith_top.winfo_exists():
            self._refresh_smith()

    # ----------------------------------------------------------------- sweep

    def _open_sweep(self):
        try:
            cable, f_MHz, length_ft, ZL = self._get_inputs()
        except (ValueError, tk.TclError):
            messagebox.showerror("Error", "Fix inputs first."); return

        dlg = tk.Toplevel(self.root)
        dlg.title("Frequency Sweep Range")
        dlg.resizable(False, False)

        frm = ttk.Frame(dlg, padding=10)
        frm.pack()

        ttk.Label(frm, text="Start (MHz):").grid(row=0, column=0, padx=4, pady=4)
        sv = ttk.Entry(frm, width=10); sv.insert(0, "1.0")
        sv.grid(row=0, column=1, padx=4)

        ttk.Label(frm, text="Stop (MHz):").grid(row=0, column=2, padx=(12, 4))
        ev = ttk.Entry(frm, width=10); ev.insert(0, "30.0")
        ev.grid(row=0, column=3, padx=4)

        def do_plot():
            try:
                f_start, f_stop = float(sv.get()), float(ev.get())
            except ValueError:
                return
            dlg.destroy()
            self._show_sweep(cable, self._cable_var.get(), f_start, f_stop, ZL, length_ft)

        ttk.Button(frm, text="Plot", command=do_plot).grid(
            row=1, column=0, columnspan=4, pady=8)

    def _show_sweep(self, cable, cable_name, f_start, f_stop, ZL, length_ft):
        top = tk.Toplevel(self.root)
        top.title(f"Sweep — {cable_name}")

        import numpy as np
        d   = sweep(cable, f_start, f_stop, ZL, length_ft)
        fs  = d["freqs"]

        fig = Figure(figsize=(11, 7))
        fig.suptitle(
            f"{cable_name}   {length_ft:.0f} ft   "
            f"ZL = {ZL.real:.1f}{ZL.imag:+.1f}j Ω",
            fontsize=11
        )

        axes = fig.subplots(2, 2)

        ax = axes[0, 0]
        ax.plot(fs, d["mll_per_100ft"], "b-")
        ax.set_title("Matched Line Loss (dB/100ft)")
        ax.set_xlabel("MHz"); ax.grid(True)

        ax = axes[0, 1]
        ax.plot(fs, d["Zo_mag"], "r-")
        ax.set_title("|Zo| (Ω)")
        ax.set_xlabel("MHz"); ax.grid(True)

        ax = axes[1, 0]
        ax.plot(fs, d["VF_eff"], "g-")
        ax.set_title("Velocity Factor")
        ax.set_xlabel("MHz"); ax.grid(True)

        ax = axes[1, 1]
        ax.plot(fs, np.clip(d["SWR_in"], 0, 50), "b-",  label="Source end")
        ax.plot(fs, np.clip(d["SWR_L"],  0, 50), "r--", label="Load end")
        ax.set_title("SWR"); ax.set_xlabel("MHz")
        ax.legend(); ax.grid(True)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=top)
        canvas.draw()
        toolbar = NavigationToolbar2Tk(canvas, top)
        toolbar.update()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        def on_close():
            plt.close(fig); top.destroy()
        top.protocol("WM_DELETE_WINDOW", on_close)

    # ----------------------------------------------------------------- Smith

    def _open_smith(self):
        if self._result is None:
            messagebox.showinfo("Smith Chart", "Run Compute first."); return

        if self._smith_top and self._smith_top.winfo_exists():
            self._smith_top.lift(); return

        self._smith_top = tk.Toplevel(self.root)
        self._smith_top.title("Smith Chart")

        self._smith_fig = Figure(figsize=(6, 6))
        self._smith_ax  = self._smith_fig.add_subplot(111)

        self._smith_canvas = FigureCanvasTkAgg(self._smith_fig, master=self._smith_top)
        self._smith_canvas.get_tk_widget().pack(fill="both", expand=True)
        toolbar = NavigationToolbar2Tk(self._smith_canvas, self._smith_top)
        toolbar.update()

        def on_close():
            plt.close(self._smith_fig)
            self._smith_top.destroy()
            self._smith_top = None
        self._smith_top.protocol("WM_DELETE_WINDOW", on_close)

        self._refresh_smith()

    def _refresh_smith(self):
        r   = self._result
        ax  = self._smith_ax
        Zo0 = r["cable"]["Zo"]

        ax.clear()
        _draw_smith_grid(ax, Zo0)

        GL  = r["Gamma_L"]
        Gin = r["Gamma_in"]

        ax.plot(GL.real, GL.imag, "ro", markersize=11, zorder=5,
                label=f"Load   Γ={abs(GL):.3f} ∠{math.degrees(cmath.phase(GL)):.1f}°")
        ax.plot(Gin.real, Gin.imag, "b^", markersize=10, zorder=5,
                label=f"Source Γ={abs(Gin):.3f} ∠{math.degrees(cmath.phase(Gin)):.1f}°")
        ax.legend(loc="lower right", fontsize=8)

        ax.set_title(
            f"Smith Chart — {self._cable_var.get()}   {r['f_MHz']:.3f} MHz",
            fontsize=10
        )
        self._smith_canvas.draw()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _usage():
    print("Usage:")
    print("  tldetails.py                            # GUI (default)")
    print("  tldetails.py --cli                      # interactive CLI")
    print("  tldetails.py --list                     # list cables")
    print("  tldetails.py CABLE f_MHz len_ft [R [X]] # single-shot")
    print()
    print("Examples:")
    print("  tldetails.py 'LMR-400' 14.2 100 50 0")
    print("  tldetails.py 'RG-8X'   28.0  50 75 25")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args and _GUI_AVAILABLE:
        root = tk.Tk()
        app  = TLDetailsGUI(root)
        root.mainloop()

    elif not args:
        print("tkinter / matplotlib not available — falling back to CLI.")
        try:
            interactive()
        except KeyboardInterrupt:
            print("\nBye.")

    elif args[0] in ("-h", "--help"):
        _usage()

    elif args[0] == "--cli":
        try:
            interactive()
        except KeyboardInterrupt:
            print("\nBye.")

    elif args[0] == "--list":
        print(f"\n{'Cable':<28} {'Zo':>6}  {'VF':>6}  {'K0':>8}  {'K1':>8}  {'K2':>10}")
        print("-" * 72)
        for name in sorted(CABLES.keys()):
            c = CABLES[name]
            print(f"{name:<28} {c['Zo']:>6.1f}  {c['VF']:>6.3f}  "
                  f"{c['K0']:>8.5f}  {c['K1']:>8.5f}  {c['K2']:>10.6f}")

    else:
        cable_name = args[0]
        if cable_name not in CABLES:
            print(f"Unknown cable: '{cable_name}'  (use --list to see options)")
            sys.exit(1)
        try:
            f_MHz     = float(args[1])
            length_ft = float(args[2])
            ZL_r      = float(args[3]) if len(args) > 3 else 50.0
            ZL_i      = float(args[4]) if len(args) > 4 else 0.0
        except (IndexError, ValueError):
            _usage(); sys.exit(1)

        result = analyze(CABLES[cable_name], f_MHz, complex(ZL_r, ZL_i), length_ft)
        print_analysis(result, cable_name)
