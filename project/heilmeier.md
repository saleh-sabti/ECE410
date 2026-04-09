# Heilmeier Questions
ECE 410/510 Spring 2026 | Saleh Sabti  
Project: Echo Detection Chiplet

---

## Q1: What are you trying to do?

Build a fixed-function chiplet that detects acoustic echo in real-time voice calls. It takes two 16-bit PCM audio streams (far-end reference, near-end mic) and outputs one bit per 8 ms window: echo present or not. No CPU in the detection path.

The dominant kernel is normalized cross-correlation: three dot-product accumulators over a 128-sample window (384 multiply-accumulate operations per window, all independent). The chiplet computes all 384 MACs in one clock cycle using a parallel MAC array, then normalizes and thresholds the result.

---

## Q2: What is done today and what are the limits?

Software echo detection runs a normalized cross-correlation loop on a CPU. Profiling `echo_detect.py` on an Intel Core Ultra 7 155H over 10 runs shows:

- `normalized_xcorr` accounts for **69% of total runtime**, 87% of detection loop (dominant kernel)
- Median wall-clock: **260 ms** to process 2 s of audio (31,872 windows)
- Arithmetic intensity: **0.747 FLOP/byte**, memory-bound on this CPU (ridge = 3.86 FLOP/byte)
- Attainable throughput: ~89 GFLOP/s (bandwidth ceiling)

Three limits: latency (285 ms end-to-end is too slow for real-time gating), power (a P-core running the detection loop draws far more than a fixed circuit), and CPU load (the loop competes with audio tasks and causes jitter). At 0.747 FLOP/byte, the software wastes most of its compute budget waiting on DRAM.

---

## Q3: What is your approach and why is it better?

A dedicated chiplet with N=128 parallel MACs and on-chip shift register storage for both sample windows. The shift registers hold 128 reference and 128 mic samples on-chip; a new sample shifts in each clock, the oldest drops off. No DRAM access during detection.

On-chip bandwidth: 128 MACs × 2 operands × 4 bytes × 500 MHz = 512 GB/s. Peak compute: 128 GFLOP/s. Ridge point: 0.25 FLOP/byte. The kernel's AI = 0.747 > 0.25, so the chiplet is **compute-bound**.

Attainable throughput: 128 GFLOP/s versus 89 GFLOP/s in software. Latency per window: 2 ns at 500 MHz versus 8.8 µs in software. The algorithm has no branching, fixed window size, and regular data access, which is the profile fixed silicon handles well.
