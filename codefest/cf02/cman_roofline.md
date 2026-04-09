# CF02 CMAN — Roofline Construction and Kernel Classification
ECE 410/510 Spring 2026 | Saleh Sabti

**Hardware spec:** Peak compute = 10 TFLOPS (FP32), Peak DRAM bandwidth = 320 GB/s  
**Ridge point:** 10,000 / 320 = **31.25 FLOP/byte**

---

## Roofline Diagram

```
GFLOP/s
  |
10000 |--------------------*---------[Kernel A ~10000 GFLOP/s]----------
      |               /   .
      |              / BW Limit 320 GB/s
 1000 |             /
      |            /
  100 |           /
      |          /
   10 |----*----/   [Kernel B ~26.7 GFLOP/s]
      |   .    /
    1 |       /
      |______________________________________
       0.01  0.1   1    10   100  1000   FLOP/byte
                              ^
                         (31.25) ridge point
```

---

## Kernel A — Dense GEMM (1024 × 1024)

Two FP32 matrices of size 1024×1024 multiplied together (square matmul).

**FLOPs:**

FLOPs = 2 × N³ = 2 × 1024³ = **2,147,483,648 FLOPs = 2,147 GFLOPs**

**Byte transfers** (all three matrices A, B, C loaded/stored from DRAM, no reuse):

Bytes = 3 × (1024 × 1024 × 4 bytes/element) = 3 × 4,194,304 = **12,582,912 bytes = 12.58 MB**

**Arithmetic intensity:**

AI = 2,147,483,648 / 12,582,912 = **170.7 FLOP/byte**

**Classification:** AI = 170.7 > ridge = 31.25 → **Compute-bound**

**Attainable performance:** Compute ceiling = **10,000 GFLOP/s**

**Architectural recommendation:** Since the kernel is compute-bound, increasing memory bandwidth won't help. The better improvement is more FP32 compute throughput — more cores or higher clock frequency.

---

## Kernel B — Vector Add (N = 4,194,304)

Two FP32 vectors of length 4,194,304 added element-wise.

**FLOPs:**

FLOPs = 4,194,304 × 1 = **4,194,304 FLOPs = 4.194 MFLOPs**

**Byte transfers** (two input vectors read, one output written, no reuse):

Bytes = 3 × (4,194,304 × 4 bytes/element) = **50,331,648 bytes = 50.3 MB**

**Arithmetic intensity:**

AI = 4,194,304 / 50,331,648 = **0.083 FLOP/byte**

**Classification:** AI = 0.083 < ridge = 31.25 → **Memory-bound**

**Attainable performance:** AI × Peak BW = 0.083 × 320 = **26.7 GFLOP/s**

**Architectural recommendation:** Since the kernel is memory-bound, more compute cores won't help. The better improvement is higher memory bandwidth — faster DRAM, wider bus, or on-chip caching of the vectors.
