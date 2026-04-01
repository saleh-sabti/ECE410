# ResNet-18 Profiling Analysis
ECE 410/510 Spring 2026 — Codefest 1 CLLM

## Top 5 MAC-Intensive Layers

| Rank | Layer Name       | Kernel | Output Shape       | MACs        | Params  |
|------|-----------------|--------|--------------------|-------------|---------|
| 1    | Conv2d: 1-1     | 7×7    | [1, 64, 112, 112]  | 118,013,952 | 9,408   |
| 2    | Conv2d: 3-1     | 3×3    | [1, 64, 56, 56]    | 115,605,504 | 36,864  |
| 3    | Conv2d: 3-4     | 3×3    | [1, 64, 56, 56]    | 115,605,504 | 36,864  |
| 4    | Conv2d: 3-7     | 3×3    | [1, 64, 56, 56]    | 115,605,504 | 36,864  |
| 5    | Conv2d: 3-10    | 3×3    | [1, 64, 56, 56]    | 115,605,504 | 36,864  |

> Note: Ranks 2–5 are a sample from 13 Conv2d layers that all achieve 115,605,504 MACs.
> The 7×7 stem layer (Conv2d: 1-1) is the single most MAC-intensive.

---

## Arithmetic Intensity — Most MAC-Intensive Layer (Conv2d: 1-1)

**Layer:** First convolutional layer, 7×7 kernel, 3 → 64 channels, stride 2, output 112×112.

### FLOPs
```
MACs = 118,013,952
FLOPs = 2 × MACs = 236,027,904
```

### Memory traffic (no reuse, all from DRAM, FP32 = 4 bytes)

**Weights:**
```
params = 64 × 3 × 7 × 7 = 9,408
weight bytes = 9,408 × 4 = 37,632 bytes
```

**Activations:**
```
input:  3 × 224 × 224 = 150,528 values → 150,528 × 4 = 602,112 bytes
output: 64 × 112 × 112 = 802,816 values → 802,816 × 4 = 3,211,264 bytes
activation bytes = 602,112 + 3,211,264 = 3,813,376 bytes
```

**Total memory traffic:**
```
total bytes = 37,632 + 3,813,376 = 3,851,008 bytes
```

### Arithmetic Intensity
```
AI = FLOPs / bytes = 236,027,904 / 3,851,008 ≈ 61.3 FLOP/byte
```

This layer is **compute-bound** on most hardware. A typical CPU has a memory bandwidth of ~50 GB/s
and a ridge point around 10–20 FLOP/byte, so at 61.3 FLOP/byte this layer sits well above the ridge
point — it can keep compute units busy if weights fit in cache.
