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

- `normalized_xcorr` accounts for **86% of runtime** (dominant kernel)
- Median wall-clock: **280 ms** to process 2 s of audio (31,872 windows)
- Arithmetic intensity: **0.747 FLOP/byte** — memory-bound on this CPU (ridge = 6.74 FLOP/byte)
- Attainable throughput: ~51 GFLOP/s (bandwidth ceiling, not compute ceiling)

The limits are three: latency (285 ms end-to-end is not usable for real-time gating), power (a P-core running the detection loop draws far more than a dedicated circuit), and CPU load (the detection loop competes with other audio tasks and causes jitter). The memory-bound classification means the software version is wasting most of its compute capacity waiting on DRAM.

---

## Q3: What is your approach and why is it better?

A dedicated chiplet with N=128 parallel MACs and on-chip shift register storage for both sample windows. The shift registers hold 128 reference and 128 mic samples on-chip; a new sample shifts in each clock, the oldest drops off. No DRAM access during detection.

This changes the bound. On-chip bandwidth: 128 MACs × 2 operands × 4 bytes × 500 MHz = 512 GB/s. Peak compute: 128 GFLOP/s. Ridge point: 0.25 FLOP/byte. The kernel's AI = 0.747 > 0.25, so the chiplet operates **compute-bound** — the opposite of the software baseline.

Attainable throughput: 128 GFLOP/s (at the compute ceiling), versus 51 GFLOP/s for the CPU (at the bandwidth ceiling). Latency per window: 1 clock cycle = 2 ns at 500 MHz, versus ~8.8 µs per window in software. The hardware argument holds because the algorithm has no branching, fixed window size, and perfectly regular data access — exactly the profile custom silicon handles well.
