# CMAN — Workload Accounting
**ECE 410/510 | Codefest 1 | Spring 2026**

Network: [784 → 256 → 128 → 10] | Batch size: 1 | FP32 (4 bytes) | No biases

---

## (a) MACs per Layer

| Layer | Formula | MACs |
|-------|---------|------|
| Layer 1 (784 → 256) | 784 × 256 | 200,704 |
| Layer 2 (256 → 128) | 256 × 128 | 32,768 |
| Layer 3 (128 → 10)  | 128 × 10  | 1,280  |

## (b) Total MACs

200,704 + 32,768 + 1,280 = **234,752 MACs**

## (c) Total Trainable Parameters

Same as MACs (weights only, no biases):

| Layer | Parameters |
|-------|-----------|
| Layer 1 | 784 × 256 = 200,704 |
| Layer 2 | 256 × 128 = 32,768 |
| Layer 3 | 128 × 10 = 1,280 |
| **Total** | **234,752** |

## (d) Weight Memory (FP32)

234,752 × 4 bytes = **939,008 bytes** ≈ 917 KB

## (e) Activation Memory (FP32)

Store input + all layer outputs simultaneously:

(784 + 256 + 128 + 10) × 4 bytes = 1,178 × 4 = **4,712 bytes** ≈ 4.6 KB

## (f) Arithmetic Intensity

```
AI = (2 × total MACs) / (weight bytes + activation bytes)
   = (2 × 234,752) / (939,008 + 4,712)
   = 469,504 / 943,720
   ≈ 0.497 FLOP/byte
```

**Arithmetic Intensity ≈ 0.50 FLOP/byte**

This is very low — the network is heavily memory-bound. Almost all time is spent moving weights from memory, not computing.

---

*File: `codefest/cf01/cman_workload_accounting.md`*
