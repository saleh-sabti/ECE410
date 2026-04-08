# roofline_plot.py
# Roofline analysis — Echo Detection Chiplet
# ECE 410/510 Spring 2026 | Saleh Sabti
#
# Hardware assumptions:
#   CPU  : Intel Core i7-class desktop  →  50 GB/s DRAM BW,  200 GFLOP/s peak FP32
#   Chiplet: N=128 MACs @ 500 MHz       → 512 GB/s on-chip BW, 128 GFLOP/s peak
#
# Workload: normalized cross-correlation, N=128, no cache reuse
#   FLOPs  = 2 × 12,238,848  =  24,477,696
#   Bytes  = 31,996.5 KB     =  32,764,416 bytes  (2N + 1 values × 4 bytes per window)
#   AI     = 0.747 FLOP/byte

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D

# ── Hardware specs ─────────────────────────────────────────────────────────────
CPU_BW      = 50       # GB/s   DRAM bandwidth (DDR4-3200 dual-ch)
CPU_PEAK    = 200      # GFLOP/s  peak FP32 (AVX2, single socket)
CPU_RIDGE   = CPU_PEAK / CPU_BW           # 4.0 FLOP/byte

# Echo Detection Chiplet: 128 parallel MACs @ 500 MHz
# Internal BW: 128 multipliers each need 2 values/cycle × 4 bytes × 500 MHz
N_MACS      = 128
F_CLK       = 500e6    # Hz
CHIP_PEAK   = N_MACS * F_CLK * 2 / 1e9   # GFLOP/s  (2 FLOP per MAC)   = 128
CHIP_BW     = N_MACS * 2 * 4 * F_CLK / 1e9  # GB/s on-chip shift-reg BW = 512
CHIP_RIDGE  = CHIP_PEAK / CHIP_BW         # 0.25 FLOP/byte

# ── Workload ───────────────────────────────────────────────────────────────────
AI_SW       = 0.747    # FLOP/byte  (measured from echo_detect.py)

# Attainable performance = min(peak, BW × AI)
PERF_SW_CPU   = min(CPU_PEAK,  CPU_BW  * AI_SW)   # 37.35  → memory-bound
PERF_SW_CHIP  = min(CHIP_PEAK, CHIP_BW * AI_SW)   # 128.0  → compute-bound

# ── Plot ───────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))

ai_range = np.logspace(-2, 4, 1000)

# CPU roofline
cpu_roof = np.minimum(CPU_PEAK, CPU_BW * ai_range)
ax.plot(ai_range, cpu_roof, color="#2563eb", linewidth=2.5, label="CPU roofline (Intel Core i7-class)")

# Chiplet roofline
chip_roof = np.minimum(CHIP_PEAK, CHIP_BW * ai_range)
ax.plot(ai_range, chip_roof, color="#16a34a", linewidth=2.5,
        linestyle="--", label=f"Chiplet roofline (N={N_MACS} MACs @ 500 MHz)")

# Ridge point markers
ax.axvline(CPU_RIDGE,  color="#2563eb", alpha=0.25, linewidth=1)
ax.axvline(CHIP_RIDGE, color="#16a34a", alpha=0.25, linewidth=1)

# Workload: software on CPU (memory-bound)
ax.scatter([AI_SW], [PERF_SW_CPU], s=160, color="#ea580c", zorder=5,
           marker="o", linewidths=1.5, edgecolors="white")
ax.annotate("SW baseline\n(memory-bound)\n0.747 FLOP/byte\n37.4 GFLOP/s",
            xy=(AI_SW, PERF_SW_CPU),
            xytext=(0.18, 22),
            fontsize=10, color="#ea580c", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#ea580c", lw=1.5))

# Workload: hardware chiplet (compute-bound)
ax.scatter([AI_SW], [PERF_SW_CHIP], s=160, color="#16a34a", zorder=5,
           marker="*", linewidths=1.5, edgecolors="white")
ax.annotate("HW chiplet\n(compute-bound)\n0.747 FLOP/byte\n128 GFLOP/s",
            xy=(AI_SW, PERF_SW_CHIP),
            xytext=(0.05, 160),
            fontsize=10, color="#16a34a", fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="#16a34a", lw=1.5))

# Arrow showing the improvement
ax.annotate("",
            xy=(AI_SW, PERF_SW_CHIP * 0.97),
            xytext=(AI_SW, PERF_SW_CPU * 1.05),
            arrowprops=dict(arrowstyle="->", color="#7c3aed", lw=2))
ax.text(AI_SW * 1.1, (PERF_SW_CPU * PERF_SW_CHIP) ** 0.5,
        f"3.4×\nfaster", color="#7c3aed", fontsize=10, fontweight="bold")

# AI vertical line
ax.axvline(AI_SW, color="#ea580c", alpha=0.3, linewidth=1.5, linestyle=":")

# Ridge labels
ax.text(CPU_RIDGE * 1.05,  0.035, f"CPU ridge\n{CPU_RIDGE:.0f} FLOP/byte",
        color="#2563eb", fontsize=9, alpha=0.8, va="bottom")
ax.text(CHIP_RIDGE * 0.55, 0.035, f"Chiplet\nridge {CHIP_RIDGE:.2f}",
        color="#16a34a", fontsize=9, alpha=0.8, va="bottom", ha="right")

# Ceiling labels
ax.text(50, CPU_PEAK * 1.08,  f"CPU peak: {CPU_PEAK} GFLOP/s",
        color="#2563eb", fontsize=9, alpha=0.9)
ax.text(50, CHIP_PEAK * 0.72, f"Chiplet peak: {CHIP_PEAK} GFLOP/s",
        color="#16a34a", fontsize=9, alpha=0.9)

# Regions
ax.fill_betweenx([0.01, CPU_PEAK], 0.01, CPU_RIDGE,
                  alpha=0.04, color="#2563eb")
ax.text(0.015, 0.05, "memory-bound\nregion (CPU)",
        color="#2563eb", fontsize=8, alpha=0.6)

ax.fill_betweenx([0.01, CHIP_PEAK], CPU_RIDGE, 1e4,
                  alpha=0.04, color="#16a34a")
ax.text(10, 0.05, "compute-bound\nregion",
        color="#16a34a", fontsize=8, alpha=0.6)

# Formatting
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_xlim(0.01, 1e4)
ax.set_ylim(0.01, 800)
ax.set_xlabel("Arithmetic Intensity (FLOP/byte)", fontsize=13, labelpad=8)
ax.set_ylabel("Attainable Performance (GFLOP/s)", fontsize=13, labelpad=8)
ax.set_title(
    "Roofline Model — Echo Detection Chiplet\n"
    "ECE 410/510 Spring 2026 | Saleh Sabti",
    fontsize=14, fontweight="bold", pad=14)
ax.grid(True, which="both", alpha=0.2, linestyle="--")

legend_elements = [
    Line2D([0], [0], color="#2563eb", lw=2.5, label="CPU roofline (50 GB/s, 200 GFLOP/s)"),
    Line2D([0], [0], color="#16a34a", lw=2.5, ls="--",
           label=f"Chiplet roofline (512 GB/s on-chip, {CHIP_PEAK:.0f} GFLOP/s)"),
    Line2D([0], [0], marker="o", color="w", markerfacecolor="#ea580c",
           markersize=10, label="SW baseline on CPU (memory-bound, 0.747 FLOP/byte)"),
    Line2D([0], [0], marker="*", color="w", markerfacecolor="#16a34a",
           markersize=14, label="HW chiplet (compute-bound, 0.747 FLOP/byte)"),
]
ax.legend(handles=legend_elements, fontsize=10, loc="upper left",
          framealpha=0.9, edgecolor="#e2e8f0")

# Annotation box with assumptions
note = (
    "Hardware assumptions:\n"
    f"  CPU:     DDR4-3200 2ch = {CPU_BW} GB/s,  AVX2 FP32 = {CPU_PEAK} GFLOP/s\n"
    f"  Chiplet: N={N_MACS} parallel MACs @ 500 MHz\n"
    f"           Peak = {CHIP_PEAK:.0f} GFLOP/s,  On-chip BW = {CHIP_BW:.0f} GB/s\n"
    f"  Workload: 3×N MACs/window, AI = {AI_SW} FLOP/byte (no cache reuse)"
)
ax.text(0.98, 0.02, note, transform=ax.transAxes,
        fontsize=8, va="bottom", ha="right",
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#f8fafc",
                  edgecolor="#e2e8f0", alpha=0.95))

plt.tight_layout()
plt.savefig("project/roofline.png", dpi=150, bbox_inches="tight")
print("Saved: project/roofline.png")

# Print summary
print(f"\n── Roofline Summary ──────────────────────────────────────────────")
print(f"  Workload AI           : {AI_SW} FLOP/byte")
print(f"  CPU ridge point       : {CPU_RIDGE:.1f} FLOP/byte  →  SW is MEMORY-BOUND")
print(f"  Chiplet ridge point   : {CHIP_RIDGE:.2f} FLOP/byte  →  HW is COMPUTE-BOUND")
print(f"  SW attainable (CPU)   : {PERF_SW_CPU:.1f} GFLOP/s")
print(f"  HW attainable (chip)  : {PERF_SW_CHIP:.1f} GFLOP/s")
print(f"  Throughput gain       : {PERF_SW_CHIP / PERF_SW_CPU:.1f}×")
print(f"\n  The 3.4× figure reflects compute throughput only.")
print(f"  Latency gain is larger: SW runs {3*128} serial steps per window;")
print(f"  HW fires all {N_MACS} MACs in 1 clock cycle (~{1/F_CLK*1e9:.1f} ns at 500 MHz).")
