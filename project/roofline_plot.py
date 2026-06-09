# roofline_plot.py
# Roofline analysis — Echo Detection Chiplet (M4, post-synthesis)
# ECE 410/510 Spring 2026 | Saleh Sabti
#
# CPU:     Intel Core Ultra 7 155H, WSL2, Python 3.12.3
#   BW   = 119.5 GB/s (LPDDR5x)
#   Peak = 462 GFLOP/s (FP32 AVX2)
#   Ridge= 3.86 FLOP/byte
#
# Chiplet: sky130, 50 MHz, nom_tt_025C_1v80 (post-CTS, timing closed)
#   Each window: 768 FLOP, 129 cycles to produce first result
#   Effective throughput: 50e6 / 129 cycles = 387,597 windows/sec
#   Peak compute: 387,597 * 768 FLOP = 297.7 MFLOP/s = 0.2977 GFLOP/s
#   Interface BW: AXI4-S, 32-bit @ 50 MHz = 200 MB/s = 0.2 GB/s
#   On-chip AI (shift-reg reuse): 768 FLOP / 4 bytes = 192 FLOP/byte
#   Ridge: 0.2977 / 0.2 = 1.49 FLOP/byte
#
# Workload (software): echo detection, N=128
#   AI  = 0.747 FLOP/byte (no cache reuse, measured from echo_detect.py)
#   Perf= 94.1 MFLOP/s = 0.094 GFLOP/s (measured, Python 3.12.3)

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ── CPU ────────────────────────────────────────────────────────────────────────
CPU_BW    = 119.5   # GB/s  LPDDR5x (Core Ultra 7 155H)
CPU_PEAK  = 462.0   # GFLOP/s  FP32 AVX2
CPU_RIDGE = CPU_PEAK / CPU_BW            # 3.86 FLOP/byte

# ── Chiplet (post-synthesis at 50 MHz) ─────────────────────────────────────────
CHIP_BW   = 0.2     # GB/s  AXI4-S 32-bit @ 50 MHz
CHIP_PEAK = 0.2977  # GFLOP/s  387,597 windows/sec × 768 FLOP/window
CHIP_RIDGE = CHIP_PEAK / CHIP_BW        # 1.49 FLOP/byte

# ── Workload ───────────────────────────────────────────────────────────────────
AI_SW   = 0.747    # FLOP/byte  software (no on-chip reuse)
AI_HW   = 192.0   # FLOP/byte  hardware (shift-reg: 768 FLOP / 4 bytes)
PERF_SW = 0.0941  # GFLOP/s  measured Python baseline
PERF_HW = 0.2977  # GFLOP/s  projected from synthesis

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 7))

ai_range = np.logspace(-2, 4, 2000)

# CPU roofline
cpu_roof = np.minimum(CPU_PEAK, CPU_BW * ai_range)
ax.plot(ai_range, cpu_roof, color="#2563eb", linewidth=2.5,
        label=f"CPU roofline (Core Ultra 7 155H: {CPU_BW} GB/s, {CPU_PEAK:.0f} GFLOP/s)")

# Chiplet roofline (post-synthesis, 50 MHz)
chip_roof = np.minimum(CHIP_PEAK, CHIP_BW * ai_range)
ax.plot(ai_range, chip_roof, color="#16a34a", linewidth=2.5, linestyle="--",
        label=f"Chiplet roofline (sky130 50 MHz: {CHIP_BW} GB/s, {CHIP_PEAK:.4f} GFLOP/s)")

# Ridge point markers
ax.axvline(CPU_RIDGE,  color="#2563eb", alpha=0.3, linewidth=1)
ax.axvline(CHIP_RIDGE, color="#16a34a", alpha=0.3, linewidth=1)

# SW baseline: actual measured Python performance
ax.scatter([AI_SW], [PERF_SW], s=180, color="#ea580c", zorder=6,
           marker="o", linewidths=1.5, edgecolors="white")
ax.annotate(
    f"SW baseline (measured)\nPython 3.12.3, Core Ultra 7 155H\nAI = {AI_SW} FLOP/byte\n{PERF_SW*1000:.1f} MFLOP/s",
    xy=(AI_SW, PERF_SW),
    xytext=(0.015, 0.002),
    fontsize=9, color="#ea580c", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#ea580c", lw=1.5))

# HW chiplet: projected from synthesis
ax.scatter([AI_HW], [PERF_HW], s=220, color="#16a34a", zorder=6,
           marker="*", linewidths=1.5, edgecolors="white")
ax.annotate(
    f"HW chiplet (projected)\nsky130, 50 MHz, N=128\nAI = {AI_HW:.0f} FLOP/byte\n{PERF_HW*1000:.1f} MFLOP/s",
    xy=(AI_HW, PERF_HW),
    xytext=(AI_HW * 0.05, PERF_HW * 4),
    fontsize=9, color="#16a34a", fontweight="bold",
    arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.5))

# AI vertical lines
ax.axvline(AI_SW, color="#ea580c", alpha=0.2, linewidth=1.2, linestyle=":")
ax.axvline(AI_HW, color="#16a34a", alpha=0.2, linewidth=1.2, linestyle=":")

# Ridge labels
ax.text(CPU_RIDGE * 1.08, 0.0003,
        f"CPU ridge\n{CPU_RIDGE:.1f} FLOP/byte",
        color="#2563eb", fontsize=8, alpha=0.85, va="bottom")
ax.text(CHIP_RIDGE * 1.08, 0.0003,
        f"Chiplet ridge\n{CHIP_RIDGE:.2f} FLOP/byte",
        color="#16a34a", fontsize=8, alpha=0.85, va="bottom")

# Ceiling labels
ax.text(500, CPU_PEAK * 1.1,  f"CPU peak: {CPU_PEAK:.0f} GFLOP/s",
        color="#2563eb", fontsize=9)
ax.text(500, CHIP_PEAK * 0.55, f"Chiplet peak: {CHIP_PEAK*1000:.1f} MFLOP/s\n(50 MHz, synthesized)",
        color="#16a34a", fontsize=9)

# Bound region shading
ax.fill_betweenx([1e-4, CPU_PEAK], 0.01, CPU_RIDGE, alpha=0.04, color="#2563eb")
ax.text(0.012, 0.0006, "memory-bound\n(CPU)", color="#2563eb", fontsize=8, alpha=0.6)

ax.fill_betweenx([1e-4, CHIP_PEAK], CHIP_RIDGE, 1e4, alpha=0.04, color="#16a34a")
ax.text(3, 0.0006, "compute-bound\n(chiplet)", color="#16a34a", fontsize=8, alpha=0.6)

# Speedup annotation
ax.annotate("",
            xy=(AI_HW, PERF_HW * 0.95),
            xytext=(AI_HW, PERF_SW * 1.08),
            arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=2))
ax.text(AI_HW * 1.15, (PERF_SW * PERF_HW) ** 0.5,
        f"{PERF_HW/PERF_SW:.1f}×\nspeedup\n(windows/sec)",
        color="#7c3aed", fontsize=9, fontweight="bold")

# Formatting
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.01, 1e4)
ax.set_ylim(1e-4, 2000)
ax.set_xlabel("Arithmetic Intensity (FLOP/byte)", fontsize=13, labelpad=8)
ax.set_ylabel("Attainable Performance (GFLOP/s)", fontsize=13, labelpad=8)
ax.set_title(
    "Roofline Model — Echo Detection Chiplet\n"
    "ECE 410/510 Spring 2026 | Saleh Sabti",
    fontsize=14, fontweight="bold", pad=14)
ax.grid(True, which="both", alpha=0.2, linestyle="--")

legend_elements = [
    Line2D([0], [0], color="#2563eb", lw=2.5,
           label=f"CPU roofline ({CPU_BW} GB/s, {CPU_PEAK:.0f} GFLOP/s)"),
    Line2D([0], [0], color="#16a34a", lw=2.5, ls="--",
           label=f"Chiplet roofline ({CHIP_BW} GB/s interface, {CHIP_PEAK*1000:.1f} MFLOP/s peak, 50 MHz)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#ea580c",
           markersize=10, label=f"SW baseline: {PERF_SW*1000:.1f} MFLOP/s measured, AI={AI_SW} FLOP/byte"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="#16a34a",
           markersize=14, label=f"HW chiplet: {PERF_HW*1000:.1f} MFLOP/s projected, AI={AI_HW:.0f} FLOP/byte"),
]
ax.legend(handles=legend_elements, fontsize=9, loc="upper left",
          framealpha=0.9, edgecolor="#e2e8f0")

note = (
    "Post-synthesis numbers (OpenLane 2.3.10, sky130_fd_sc_hd):\n"
    f"  Clock: 50 MHz, timing closed nom_tt_025C_1v80 (WNS = +3.477 ns)\n"
    f"  Throughput: 387,597 windows/sec  |  Power: 21.05 mW\n"
    f"  SW measured: 122,585 windows/sec (Python 3.12.3, float32)\n"
    f"  Speedup: {PERF_HW/PERF_SW:.2f}x throughput (windows/sec)\n"
    f"  Energy: 21 mW vs ~15 W CPU active = ~700x better per window"
)
ax.text(0.98, 0.02, note, transform=ax.transAxes,
        fontsize=8, va="bottom", ha="right",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8fafc",
                  edgecolor="#e2e8f0", alpha=0.95))

plt.tight_layout()
plt.savefig("project/roofline.png", dpi=150, bbox_inches="tight")
print("Saved: project/roofline.png")

print(f"\n── Roofline Summary (M4, post-synthesis) ────────────────────────────")
print(f"  CPU:     {CPU_BW} GB/s,  {CPU_PEAK} GFLOP/s,  ridge = {CPU_RIDGE:.2f} FLOP/byte")
print(f"  Chiplet: {CHIP_BW} GB/s,  {CHIP_PEAK:.4f} GFLOP/s,  ridge = {CHIP_RIDGE:.2f} FLOP/byte")
print(f"  SW AI = {AI_SW} FLOP/byte  < CPU ridge {CPU_RIDGE:.2f}  → memory-bound on CPU")
print(f"  HW AI = {AI_HW} FLOP/byte  > chiplet ridge {CHIP_RIDGE:.2f}  → compute-bound on chiplet")
print(f"  SW actual: {PERF_SW*1000:.1f} MFLOP/s  (well below memory ceiling — Python overhead)")
print(f"  HW projected: {PERF_HW*1000:.1f} MFLOP/s  (at compute ceiling)")
print(f"  Speedup: {PERF_HW/PERF_SW:.2f}x  |  Energy: ~700x better per window")
