# TLDetails — Transmission Line Details Calculator

A Python clone of [Dan Maguire (AC6LA)](https://www.ac6la.com/tldetails1.html)'s *TLDetails* Visual Basic program, which has not been updated since 2014 and requires the Windows VB6 runtime to run.

This reimplementation reproduces the same physics and covers the same cable library in pure Python, with a Tkinter GUI, an interactive CLI, and a library API you can import into your own scripts.

---

## Features

- **43 built-in cable types** — 50 Ω and 75 Ω coax (RG-58, RG-8, RG-213, LMR-series, Heliax, hardline), ladder line, open wire, and twinlead
- **Full complex transmission line model** — frequency-dependent Zo, RLGC parameters, propagation constant γ = α + jβ
- **K0/K1/K2 loss model** — matched line loss = K0 + K1·√f + K2·f (dB/100ft, f in MHz), identical to the AC6LA model
- **Both line ends** — impedance, reflection coefficient (Rho and angle), SWR, and return loss at load and source
- **Power loss breakdown** — matched line loss, additional loss due to SWR mismatch, total loss
- **Frequency sweep plots** — matched line loss, |Zo|, velocity factor, and SWR vs. frequency (embedded matplotlib with zoom/pan)
- **Smith chart** — resistance circles, reactance arcs, SWR reference circles, and markers for both line ends; updates live on recompute
- **Tkinter GUI** — auto-computes on every input change, no separate Calculate button needed
- **CLI modes** — interactive menu, single-shot command line, cable listing

---

## Requirements

- Python 3.8+
- `matplotlib` and `numpy` (for plots and Smith chart)

Tkinter ships with the standard Python distribution on most platforms. If it is missing on your Linux system:

```
sudo apt install python3-tk        # Debian / Ubuntu
sudo dnf install python3-tkinter   # Fedora
```

Install Python dependencies:

```
pip install -r requirements.txt
```

---

## Usage

### GUI (default)

```
python tldetails.py
```

Select a cable from the dropdown, enter frequency, line length, and load impedance. Results update automatically. Use **Sweep Plot** to open a frequency sweep window, or **Smith Chart** to open a live Smith chart.

### Interactive CLI

```
python tldetails.py --cli
```

### Single-shot command line

```
python tldetails.py CABLE f_MHz length_ft [R [X]]
```

`R` and `X` are the real and imaginary parts of the load impedance (default 50+0j Ω).

**Examples:**

```
python tldetails.py 'LMR-400'   14.2  100  50   0
python tldetails.py 'RG-58C/U'  146.0  50  50   0
python tldetails.py 'RG-213/U'   7.1  150  25 -30
```

### List all cables

```
python tldetails.py --list
```

---

## Cable database

| Group | Examples |
|-------|---------|
| 50 Ω coax | RG-58C/U, RG-8/U, RG-213/U, RG-174, RG-316, LMR-195/240/300/400/500/600, Belden 9913, Heliax FSJ/LDF series, hardline ½″/⅞″/1⅝″ |
| 75 Ω coax | RG-59/U, RG-6/U, RG-11/U, Belden 8241/1694A |
| Balanced | 300 Ω twinlead, 450 Ω ladder line, 600 Ω open wire |
| Custom | User-defined Zo, VF, K0, K1, K2 |

Cable parameters (Zo, VF, K0, K1, K2) are sourced from ARRL references and manufacturer data sheets. To add a cable, insert an entry in the `CABLES` dict in `tldetails.py`.

---

## Physics summary

The loss model is:

```
MLL(f) = K0 + K1·√f + K2·f    [dB/100ft, f in MHz]
```

where K0 represents DC resistance, K1 skin-effect loss, and K2 dielectric loss. RLGC parameters are derived from K0/K1/K2 together with the nominal Zo and velocity factor, giving a frequency-dependent complex characteristic impedance:

```
Zo(f) = √( (R + jωL) / (G + jωC) )
```

Input impedance of a terminated line:

```
Zin = Zo · (ZL + Zo·tanh(γl)) / (Zo + ZL·tanh(γl))
```

Additional loss due to SWR mismatch uses the Sabin/ARRL formula. All arithmetic uses Python's built-in complex numbers.

---

## As a library

```python
from tldetails import CABLES, analyze, print_analysis, sweep, plot_sweep

cable  = CABLES["LMR-400"]
result = analyze(cable, f_MHz=14.2, ZL=complex(50, 0), length_ft=100)
print_analysis(result, "LMR-400")

# Frequency sweep data (numpy arrays)
data = sweep(cable, f_start=1, f_stop=30, ZL=complex(50, 0), length_ft=100)

# Matplotlib plot
plot_sweep(cable, "LMR-400", f_start=1, f_stop=30, ZL=complex(50, 0), length_ft=100)
```

The `analyze()` return dict contains: `Zin`, `ZL`, `Gamma_in`, `Gamma_L`, `SWR_in`, `SWR_L`, `RL_in_dB`, `RL_L_dB`, `mll_per_100ft`, `mll_total_dB`, `additional_loss_dB`, `total_loss_dB`, `delay_ns`, `Zo_complex`, `gamma`, `rlgc`, and more.

---

## Acknowledgements

The original *TLDetails* program was written by Dan Maguire, AC6LA. The K0/K1/K2 loss model, cable data, and general approach follow his work. Transmission line theory follows Chipman, *Theory and Problems of Transmission Lines* (1968).

---

## License

MIT — see [LICENSE](LICENSE).
