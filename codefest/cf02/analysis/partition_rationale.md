# HW/SW Partition Rationale
ECE 410/510 Spring 2026 | Saleh Sabti  
Project: Echo Detection Chiplet

---

## (a) Which kernel to accelerate and why the roofline supports that choice

The kernel to accelerate in hardware is `normalized_xcorr` in `echo_detect.py:47`. cProfile across 10 runs shows it accounts for 86% of total runtime. It is the only loop in the algorithm: three parallel dot-product accumulators over N=128 samples. All N multiply-accumulate operations per accumulator are data-independent, so they can fire in a single clock cycle on a parallel MAC array.

The roofline confirms the choice. On the Intel Core Ultra 7 155H (119.5 GB/s DRAM, 460.8 GFLOP/s peak), the kernel sits at AI = 0.747 FLOP/byte, below the ridge at 3.86 FLOP/byte. DRAM bandwidth is the bottleneck. A chiplet with on-chip shift registers removes the DRAM traffic: both sample windows live in two N-deep shift registers, moving the kernel from memory-bound to compute-bound.

## (b) What the software baseline continues to handle

Signal acquisition and framing stay in software. The host CPU generates or receives the raw audio streams and feeds samples into the chiplet one at a time via the streaming interface. The 1-bit output decision is read back by the host and used to gate any downstream echo canceller. No part of the cross-correlation computation remains in software once the chiplet is active.

## (c) Interface bandwidth required to avoid becoming interface-bound

Audio input rate: 2 channels × 16,000 samples/s × 16 bits/sample = 512 kbps = **0.064 MB/s**.

AXI4 Stream at 100 MHz with a 32-bit data bus delivers 400 MB/s rated bandwidth.

Required bandwidth / interface bandwidth = 0.064 / 400 = 0.016% utilization.

The chiplet is not interface-bound. At minimum AXI4 Stream configuration (8-bit bus, 10 MHz), the interface delivers 10 MB/s, 156× the audio data rate.

## (d) Bound classification and whether HW changes it

On the current CPU, the kernel is **memory-bound** (AI = 0.747 < ridge = 3.86 FLOP/byte). The bottleneck is fetching 128 ref and 128 mic samples from DRAM on every window.

The hardware design eliminates this bottleneck. Shift registers hold both N-sample windows on-chip. A new sample shifts in each clock cycle; the oldest drops off. No DRAM access during detection. The chiplet's on-chip bandwidth is 128 MACs × 2 operands × 4 bytes × 500 MHz = 512 GB/s, and its compute ceiling is 128 GFLOP/s (128 MACs × 500 MHz × 2 FLOP). Ridge point = 128 / 512 = 0.25 FLOP/byte. Since AI = 0.747 > 0.25, **the HW design is compute-bound**, the opposite classification from software.
