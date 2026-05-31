# CF09 CMAN: Arithmetic Intensity of the Echo Detection Kernel

## 1. Dominant Kernel

The kernel is a sliding-window dot product. Each window computes three dot products of length N: cross-correlation (ref * mic), reference energy (ref * ref), and mic energy (mic * mic).

N = 128 samples, INT16 inputs (2 bytes each), 40-bit signed accumulator. This is a streaming sliding window, not GEMM. Each new sample pair is used for all three dot products in that window, then shifts out.

## 2. FLOPs per Window

```
FLOPs = 3 x 2N = 6 x 128 = 768 FLOPs per window  (= 384 MACs x 2)
```

## 3. Bytes Transferred

This kernel does not fit the GEMM weight-reuse pattern. Neither ref nor mic is a static weight matrix. The reuse pattern is shift-register streaming: one new sample pair enters per window step, and the previous N-1 pairs stay on chip.

**Lower bound (no on-chip reuse): load all N samples fresh each window:**

```
Bytes = N x 2 (ref) + N x 2 (mic) = 512 bytes/window
AI_lower = 768 / 512 = 1.5 FLOP/byte
```

**Upper bound (full on-chip reuse via shift registers): only 1 new pair enters per step:**

```
Bytes = 1 ref + 1 mic = 4 bytes/window
AI_upper = 768 / 4 = 192 FLOP/byte
```

## 4. Roofline

Platform: sky130 ASIC, timing closed at 50 MHz. Interface: AXI4-Stream, 32-bit TDATA.

```
Peak throughput = 768 FLOPs / 129 cycles x 50 MHz = 297.7 MOPS = 0.298 GOPS
Peak BW         = 50 MHz x 4 bytes = 200 MB/s = 0.2 GB/s
Ridge point     = 0.298 / 0.2 = 1.49 FLOP/byte
```

AI_lower = 1.5 FLOP/byte, just above the ridge: compute-bound.
AI_upper = 192 FLOP/byte, well into the compute-bound region.

With shift registers holding the window on-chip, the design operates near AI_upper. The interface is not the bottleneck.



## 5. Bottleneck and Improvement

The design is compute-bound. The MAC tree produces one result every 129 cycles at 50 MHz. The AXI4-S interface delivers 4 bytes/cycle, so it keeps up easily.

The single highest-leverage change: reduce N from 128 to 64. That cuts cycles per window from 129 to 65, doubles throughput to ~595 MOPS, and cuts cell count roughly in half. It also clears the routing congestion that caused the DRT failure in M3.
