# Arithmetic Intensity Calculation
ECE 410/510 Spring 2026 | Saleh Sabti  
Algorithm: Normalized cross-correlation echo detection (`project/echo_detect.py`)

---

## Dominant Kernel

`normalized_xcorr` in `echo_detect.py:47` accounts for 69% of total program runtime and 87% of streaming detection time across 10 profiled runs (see `project_profile.txt`). It is the inner correlation loop, called once per audio window.

---

## FLOPs Count

The kernel runs three accumulators over N=128 samples:

```
for r, m in zip(ref_win, mic_win):
    dot        += r * m        # 1 mul + 1 add = 2 FLOP
    energy_ref += r * r        # 1 mul + 1 add = 2 FLOP
    energy_mic += m * m        # 1 mul + 1 add = 2 FLOP
```

FLOPs per window = 3 accumulators × 2 FLOP/MAC × N samples  
= 3 × 2 × 128 = **768 FLOP/window**

Plus 1 sqrt + 1 divide (post-loop) = ~770 FLOP/window (negligible, omitted below)

Total windows = total_samples - N = 32,000 - 128 = 31,872

**Total FLOPs = 768 × 31,872 = 24,477,696 FLOP**

---

## Bytes Transferred (DRAM, no reuse)

Per window, all operands load from DRAM with no cache reuse:

| Operand | Count | Bytes (FP32 = 4 B) |
|---------|-------|---------------------|
| ref_win | N = 128 values | 512 B |
| mic_win | N = 128 values | 512 B |
| Output (corr scalar) | 1 value | 4 B |

Bytes per window = (128 + 128 + 1) × 4 = 257 × 4 = **1,028 bytes/window**

Total bytes = 1,028 × 31,872 = **32,764,416 bytes** (31,996.5 KB)

---

## Arithmetic Intensity

AI = Total FLOPs / Total bytes

= 24,477,696 / 32,764,416

**AI = 0.747 FLOP/byte**

---

## Roofline Classification

Target platform: Intel Core Ultra 7 155H (Lenovo Yoga Pro 7 14IMH9)  
- Peak DRAM bandwidth: **119.5 GB/s** (LPDDR5X-7467, 2-channel 128-bit bus: 7467 MT/s × 16 B)  
- Peak FP32 throughput: 460.8 GFLOP/s (6 P-cores × 4.8 GHz boost × 16 FLOP/cycle, AVX2 FMA)  
- Ridge point: 460.8 / 119.5 = **3.86 FLOP/byte**

AI = 0.747 < ridge = 3.86 → **kernel is memory-bound on this CPU**

Attainable performance = min(460.8, 119.5 × 0.747) = min(460.8, 89.3) = **89.3 GFLOP/s**
