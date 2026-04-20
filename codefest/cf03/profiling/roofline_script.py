#!/usr/bin/env python3
# Generates gemm_roofline.png for CF3.
# Edit NAIVE_GFLOPS and TILED_GFLOPS with measured values after running the kernels.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys

# RTX 4050 Laptop GPU specs
PEAK_COMPUTE = 3588.0   # GFLOP/s FP32
PEAK_BW      = 192.0    # GB/s
RIDGE        = PEAK_COMPUTE / PEAK_BW  # 18.7 FLOP/byte

# 1024x1024 FP32 GEMM
N = 1024
FLOPS = 2.0 * N**3  # 2.147G

# Arithmetic intensities
# Naive: each element of A and B accessed N times, no reuse
# Total bytes = 2 * N^2 * N * 4 = 8*N^3
AI_NAIVE  = FLOPS / (8.0 * N**3)   # 0.25 FLOP/byte

# Tiled T=8: each element loaded N/T times instead of N times
# Total bytes = 8*N^3/T
T = 8
AI_TILED  = FLOPS / (8.0 * N**3 / T)  # 2.0 FLOP/byte

# Measured performance — update these after running the kernels
NAIVE_GFLOPS = float(sys.argv[1]) if len(sys.argv) > 1 else 35.0   # placeholder
TILED_GFLOPS = float(sys.argv[2]) if len(sys.argv) > 2 else 280.0  # placeholder

# Roofline
ai_range = np.logspace(-2, 3, 500)
memory_roof  = PEAK_BW * ai_range
compute_roof = np.full_like(ai_range, PEAK_COMPUTE)
roofline     = np.minimum(memory_roof, compute_roof)

fig, ax = plt.subplots(figsize=(8, 5))
ax.loglog(ai_range, roofline, 'k-', linewidth=2, label='RTX 4050 Laptop roofline')
ax.axvline(RIDGE, color='gray', linestyle='--', linewidth=1, alpha=0.7, label=f'Ridge = {RIDGE:.1f} FLOP/byte')

# Kernel points (AI, achieved GFLOP/s)
ax.scatter(AI_NAIVE, NAIVE_GFLOPS, color='red',  s=100, zorder=5)
ax.annotate(f'Naive\n{NAIVE_GFLOPS:.0f} GFLOP/s\nAI={AI_NAIVE:.2f}',
            xy=(AI_NAIVE, NAIVE_GFLOPS), xytext=(AI_NAIVE*3, NAIVE_GFLOPS*0.5),
            arrowprops=dict(arrowstyle='->', color='red'), color='red', fontsize=9)

ax.scatter(AI_TILED, TILED_GFLOPS, color='blue', s=100, zorder=5)
ax.annotate(f'Tiled (T=8)\n{TILED_GFLOPS:.0f} GFLOP/s\nAI={AI_TILED:.2f}',
            xy=(AI_TILED, TILED_GFLOPS), xytext=(AI_TILED*3, TILED_GFLOPS*0.5),
            arrowprops=dict(arrowstyle='->', color='blue'), color='blue', fontsize=9)

ax.set_xlabel('Arithmetic Intensity (FLOP/byte)', fontsize=11)
ax.set_ylabel('Performance (GFLOP/s)', fontsize=11)
ax.set_title('Roofline — 1024x1024 FP32 GEMM on RTX 4050 Laptop GPU', fontsize=11)
ax.legend(fontsize=9)
ax.set_xlim(1e-2, 1e3)
ax.set_ylim(1, PEAK_COMPUTE * 3)
ax.grid(True, which='both', alpha=0.3)

out = 'codefest/cf03/profiling/gemm_roofline.png'
plt.tight_layout()
plt.savefig(out, dpi=150)
print(f"Saved {out}")
