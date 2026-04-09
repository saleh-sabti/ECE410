# CF02 CMAN — Roofline Construction and Kernel Classification
Saleh Sabti | ECE 410 | Spring 2026

**Hardware:** Peak compute = 10 TFLOPS (FP32), Peak DRAM BW = 320 GB/s, Ridge = 10,000 / 320 = **31.25 FLOP/byte**

---

## Kernel A — Dense GEMM (1024 × 1024)

FLOPs = 2 × N³ = 2 × 1024³ = 2,147,483,648 FLOPs = **2,147 GFLOPs**

Byte transfers (A, B, C all loaded/stored, no reuse) = 3 × (1024 × 1024 × 4) = **12.58 MB**

AI = 2,147,483,648 / 12,582,912 = **170.7 FLOP/byte**

AI = 170.7 > 31.25 → **Compute-bound** | Attainable = compute ceiling = **10,000 GFLOP/s**

Architectural recommendation: since kernel is compute-bound, more memory BW won't help. Better to add more FP32 compute throughput (more cores, higher clock).

---

## Kernel B — Vector Add (N = 4,194,304)

FLOPs = 4,194,304 × 1 = **4.194 MFLOPs**

Byte transfers (2 inputs read, 1 output written, no reuse) = 3 × (4,194,304 × 4) = **50.3 MB**

AI = 4,194,304 / 52,428,800 = **0.083 FLOP/byte**

AI = 0.083 < 31.25 → **Memory-bound** | Attainable = AI × Peak BW = 0.083 × 320 = **26.7 GFLOP/s**

Architectural recommendation: since kernel is memory-bound, more cores won't help. Better to increase memory bandwidth (wider bus, faster DRAM).
