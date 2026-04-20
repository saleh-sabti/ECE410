# CMAN DRAM Traffic Analysis
**ECE 410/510 | Codefest 3 | Spring 2026**

N=32, T=8, FP32 (4 bytes/element), BW=320 GB/s, Compute=10 TFLOPS

---

## (a) Naive DRAM Traffic

```
Traffic = (2N³ + N²) × 4 bytes
        = (2×32³ + 32²) × 4
        = 266,240 bytes ≈ 260 KB
```

---

## (b) Tiled DRAM Traffic (T=8)

```
Traffic = 2N² × 4 bytes
        = 2×32² × 4
        = 8,192 bytes ≈ 8 KB
```

---

## (c) Traffic Ratio

```
Ratio = naive / tiled = 2N³ / 2N² = N = 32
```

> **The ratio equals N because in the naive case each element of A and B is loaded from DRAM N times (once per output row or column), while tiling reduces this to a single load per element.**

---

## (d) Execution Times

### Naive (memory-bound)
```
Memory time = 266,240 bytes / (320 × 10⁹ B/s) ≈ 0.83 µs
Compute time = 65,536 FLOPs / (10 × 10¹² FLOP/s) ≈ 0.0066 µs

Memory time >> Compute time => MEMORY-BOUND
```

### Tiled (compute-bound)
```
Memory time = 8,192 bytes / (320 × 10⁹ B/s) ≈ 0.026 µs
Compute time ≈ 0.0066 µs

Compute time > Memory time => COMPUTE-BOUND
```

