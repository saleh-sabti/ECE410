# Design Justification Report
ECE 410/510 Spring 2026 | Saleh Sabti
Project: Echo Detection Chiplet

---

## Problem and Motivation

The target kernel is normalized cross-correlation between two 16-bit PCM audio streams: a far-end reference signal and a near-end microphone capture. The output is one bit per 8 ms window: echo present or not. No CPU in the detection path.

Profiling `echo_detect.py` (cProfile, Intel Core Ultra 7 155H, WSL2) shows `normalized_xcorr` is 69% of total runtime and 87% of the streaming detection loop. The software baseline processes 2 s of audio (31,872 windows, N=128) in a median of 260 ms over 10 runs, producing 122,585 windows/sec. Arithmetic intensity on the CPU is 0.747 FLOP/byte, below the CPU ridge point of 3.86 FLOP/byte, so the kernel is memory-bound: attainable throughput is capped by DRAM bandwidth, not compute.

Three practical limits drive the hardware case. Latency: 260 ms for 2 s of audio is 7.7x real-time, fine for batch but not acceptable for gating or adaptive filtering where the decision must precede the next window. Power: a P-core running the inner loop draws ~15 W; a fixed circuit drawing 21 mW is ~700x more efficient per window. Jitter: the detection loop competes with audio I/O and OS scheduling, causing variable latency per window.

The kernel maps well to fixed silicon. Every window is the same operation: three dot-product accumulators over N=128 samples, all independent across the window. No branching. Fixed memory pattern. That profile is what custom silicon handles best.

---

## Roofline Analysis

The dominant kernel has three dot products per window: Σ ref[i]·mic[i], Σ ref[i]², Σ mic[i]². Each dot product is 2N FLOPs, so one window is 768 FLOP total.

Two arithmetic intensity bounds apply. The lower bound (no on-chip reuse) loads both buffers fresh each window: 2 buffers × 128 samples × 2 bytes = 512 bytes, giving AI = 768/512 = 1.5 FLOP/byte. The upper bound (shift-register reuse) loads only the two new samples per window: 4 bytes, giving AI = 768/4 = 192 FLOP/byte. Reality sits between these extremes.

The chiplet uses shift registers, so only the two incoming samples cross the interface per clock. The remaining N-1 samples stay on chip. This pushes effective AI toward the upper bound. In steady-state streaming, the interface moves 4 bytes per clock while all 128 MACs fire simultaneously.

Platform ridge points:
- CPU (Core Ultra 7 155H): peak BW 119.5 GB/s, peak compute ~462 GFLOP/s, ridge = 3.86 FLOP/byte. Software at AI=0.747 is memory-bound.
- Hardware chiplet (sky130, 50 MHz, AXI4-S at 200 MB/s): peak compute 297.7 MOPS, ridge = 1.49 FLOP/byte. Both AI bounds (1.5 and 192) exceed the ridge, so the chiplet is compute-bound across its full operating range.

This shaped the architecture directly. Because the hardware is compute-bound, more memory bandwidth does not improve throughput. The optimization axis is clock rate or reduced N, not bandwidth. Using SRAM instead of shift registers would lower AI toward 1.5 FLOP/byte and risk crossing the ridge. On-chip shift registers bypass that risk.

---

## Precision and Data Format

Samples are signed 16-bit integer (INT16). Standard audio PCM at 16 kHz is INT16 at the ADC and codec: no conversion needed at the chiplet boundary. INT16 covers 96 dB dynamic range. INT8 drops to 48 dB and increases false negatives under low-SNR conditions. FP32 quadruples byte traffic (2 bytes vs 8 bytes per sample pair) with no accuracy benefit since the signal is already quantized to 16-bit resolution at the ADC.

Accumulators are 40-bit signed (ACCW=40). One INT16 product fits in 30 bits (32767² ≈ 1.07×10⁹). Summing 128 products gives at most 1.37×10¹¹, requiring 37 bits. 40 bits adds 3 bits of headroom and aligns to a 5-byte boundary. A 32-bit accumulator overflows for large correlated signals.

Error analysis: 100 random INT16 test vectors (samples from [-1000, 1000]) show max absolute error of 0 between the 40-bit DUT and a Python float64 reference. Integer MAC over a 40-bit register is exact for these inputs. No rounding occurs because there is no division or square root in the accumulation path.

Normalization (dividing by sqrt(ref_energy × mic_energy)) was not implemented in hardware. The comparator uses an unnormalized threshold set in accumulated units. This defers a hardware sqrt at the cost of requiring threshold calibration per signal amplitude. For constant-amplitude test signals, the threshold is exact. For variable-amplitude audio, the threshold must be tuned per session, which is acceptable at 8 ms windows where signal statistics are roughly stationary.

---

## Dataflow and Architecture

The dataflow pattern is streaming input-stationary. Both the reference and microphone buffers are shift registers clocked by AXI4-Stream TVALID. Each new sample pair shifts in at one end; the oldest sample drops off the other. No random-access memory. No address generation. The buffer state is always the current N-sample window.

Compute path inside `compute_core`:
1. All N multiplications fire combinationally in the same clock cycle. Each MAC unit takes one element from ref_buf and the corresponding element from mic_buf.
2. Products reduce through a 7-level binary adder tree (128→64→32→16→8→4→2→1) to produce acc_cross, acc_ref, and acc_mic (three parallel trees, same structure).
3. A 40-bit signed comparator checks acc_cross >= threshold and drives echo_det.
4. echo_det and valid_out register on the rising edge of the clock after N+1 valid input beats (N to fill the shift register, one more to produce the first result).

The AXI4-Stream slave (`axi4s_rx`) unpacks TDATA[31:16] as ref_sample and TDATA[15:0] as mic_sample on each TVALID beat, drives valid_in, and feeds the samples into compute_core. The threshold is a static input port.

Total latency from first TVALID to first valid output: N+1 = 129 clock cycles = 2.58 µs at 50 MHz. This is well under the 8 ms window period, so the chiplet keeps up with real-time audio without backpressure.

No pipeline registers exist inside the MAC path. All 128 multiplications and the full adder tree are one combinational stage. This keeps the RTL simple and verifiable. The cost is a long critical path (86.7 ns at nom_tt before CTS optimization), which limited timing to 50 MHz. Adding pipeline registers after adder level 4 would allow 100 MHz but adds one cycle of latency and complicates verification. For a 16 kHz audio application, 50 MHz already runs 3,125x faster than the sample rate: the headroom is sufficient.

---

## Hardware Interface

Interface: AXI4-Stream (AMBA standard, TVALID/TREADY handshake).

Required bandwidth: 2 channels × 16,000 samples/s × 2 bytes = 64,000 bytes/s = 0.064 MB/s. AXI4-Stream at 100 MHz, 32-bit bus is rated at 400 MB/s. Margin: 6,250x. The interface is never the bottleneck.

Roofline check: at 50 MHz (32-bit bus, one transfer per cycle) the interface moves 200 MB/s. Ridge = 297.7 MOPS / 200 MB/s = 1.49 FLOP/byte. Audio data arrives at 0.064 MB/s, far below 200 MB/s. The design is compute-bound, not interface-bound.

Why AXI4-Stream over alternatives:
- I2C Fast (0.05 MB/s): borderline for two-channel audio, no streaming semantics.
- SPI: sufficient bandwidth, no native backpressure, requires custom glue on host side.
- PCIe: overkill bandwidth, adds endpoint IP area and power not justified for audio.
- AXI4-Lite: control plane only, no streaming semantics.
- AXI4-Stream: unidirectional streaming, TVALID/TREADY maps directly to the sample-by-sample shift register input, Zynq-class SoCs expose it natively with no custom host glue.

Timing: the interface module (`axi4s_rx`) adds roughly 10 flip-flops and a small decoder on top of compute_core. Its area contribution is negligible (< 0.01% of total liberty area 88,038 µm²). Post-CTS timing for the full top-level design closed at nom_tt_025C_1v80 with WNS = 0 ns, worst slack = +3.477 ns. The interface logic is not the critical path; the adder tree in compute_core is.

---

## Verification

Three testbench suites were run with Icarus Verilog 12.0.

**`tb_compute_core.sv` (M2): 2/2 PASS.**
Test 1: ref=1, mic=1 for all 128 samples. Expected acc_cross = 128. DUT output: 128. Error: 0.
Test 2: ref=1, mic=-1 for all 128 samples. Expected acc_cross = -128. DUT output: -128. Error: 0.
Both tests confirmed echo_det asserts when acc_cross crosses the threshold and stays low otherwise.

**`tb_interface.sv` (M2): 4/4 PASS.**
Tests cover: TVALID asserted before TREADY (backpressure hold), normal handshake (both asserted), correct unpacking of TDATA into ref_sample and mic_sample, and valid_in only asserted on completed handshakes. TDATA[31:16] maps to ref and [15:0] to mic.

**`tb_top.sv` (M3): 2/2 PASS.**
End-to-end co-simulation with 130 TVALID beats (129 needed to fill the shift register and produce the first result, plus one setup beat). Test 1: all samples = 1 (fully correlated), echo_det asserted at cycle 130. Test 2: threshold above maximum possible accumulator value, echo_det stays low. Waveform in `project/m3/sim/cosim_waveform.png`.

Random error analysis (100 test vectors, INT16 samples in [-1000, 1000]): max absolute error between DUT acc_cross and Python float64 reference = 0. Integer multiply-accumulate over 40-bit registers is exact for this input range.

---

## Synthesis Results

Tool: OpenLane 2.3.10, sky130_fd_sc_hd, run RUN_2026-05-21_20-44-53.
Clock target: 20 ns (50 MHz). Die: 2380 × 2391 µm.

**Area:**
- Yosys synthesis: 222,941 standard cells, liberty area 88,038 µm²
- Placed instance area: 1,977,000 µm² (302,820 total cells including tap/fill)
- Core utilization: 35.2%
- Sequential cells: 4,139 flip-flops (2 × 128 × 16 shift register bits + control)
- Dominant cell types: AND/NAND (adder carry chains), XOR/XNOR (adder sum bits), dfxtp_2 (shift register FFs)

**Timing:**
- Post-CTS, nom_tt_025C_1v80: WNS = 0 ns, worst setup slack = +3.477 ns. Timing CLOSED at 50 MHz.
- Hold: WNS = 0 ns, no violations.
- nom_ss_100C_1v60 (slow corner): WNS = -134 ns. Timing not closed.
- Critical path: ref_buf[127] FF → fanout buffers → 16×16 multiplier → 7-level adder tree → echo_det FF. Pre-CTS nom_tt delay was 86.7 ns. The OpenROAD resizer closed nom_tt by inserting buffer trees on high-fanout shift-register nets and resizing cells on the path.

**Power (nom_tt_025C_1v80, placed netlist):**
- Total: 21.05 mW
- Clock tree: 12.1 mW (57.3%)
- Sequential: 8.2 mW (39.2%)
- Combinational (MAC tree): 0.74 mW (3.5%)

Clock tree dominates because 4,139 flip-flops all toggle every cycle. The MAC tree itself is cheap: only 3.5% of power for the element doing all the computation. This is a known tradeoff in shift-register-based designs on sky130.

**Routing:** Detailed routing failed at DRT-0349 (LEF58_ENCLOSURE with no CUTCLASS not supported for layer mcon, OpenLane 2.3.10 / sky130A PDK compatibility issue). Global routing completed with 0 overflow. Detailed routing reached 20% with 0 violations before stopping. Placement and CTS completed cleanly. Post-route timing and parasitic-extracted power are not available.

---

## Benchmark Results

**Software baseline (M1, measured):**
Platform: Intel Core Ultra 7 155H, WSL2, Python 3.12.3.
Script: `project/echo_detect.py`, explicit MAC loop, float32, no NumPy in the core loop.
Input: 2 s at 16 kHz, N=128, 31,872 windows.
Median wall-clock: 260 ms (10 runs).
Throughput: 122,585 windows/sec, 94.1 MFLOP/s.
AI: 0.747 FLOP/byte. Memory-bound on CPU.

**Hardware accelerator (projected from synthesis):**
Clock: 50 MHz (timing closed nom_tt post-CTS).
Cycles per window: N+1 = 129.
Throughput: 50×10⁶ / 129 = 387,597 windows/sec (projected).
Execution time for 31,872 windows: 82.2 ms (projected).
Speedup: 387,597 / 122,585 = **3.16x** (projected).
Energy: 21.05 mW / 387,597 windows/sec = 54.3 nJ/window (projected).
Memory footprint: ~10 KB on-chip.

All hardware numbers are projected from synthesis. Detailed routing failed, so post-route simulation was not completed. Converting to measured results requires: routing in a compatible PDK build, post-route parasitic extraction (OpenRCX), and re-running STA on the annotated netlist.

The speedup is against an interpreted Python baseline. An optimized C or NumPy baseline would be faster, which would narrow the throughput gap. The energy comparison is more meaningful and robust: 21 mW vs ~15 W CPU active is ~700x regardless of the exact software throughput.

---

## What Did Not Work

**Routing failed (DRT-0349).** The most consequential failure. OpenLane 2.3.10's OpenROAD router does not support LEF58_ENCLOSURE via rules for layer mcon in sky130A. This is a tool-PDK version mismatch, not a design error. Placement was clean, timing closed at CTS, and global routing had 0 overflow. The same error appeared in CF7 on a smaller design. The fix requires either a newer OpenROAD build with LEF58_ENCLOSURE support or a patched sky130A LEF, neither of which was available in the course Docker image.

**Slow-corner timing unclosed.** At nom_ss_100C_1v60, WNS = -134 ns. The design only meets timing at nom_tt. A real tapeout would require pipelining the adder tree (halves path depth, allows 100 MHz) or accepting a reduced operating frequency at worst-case PVT.

**Normalization not implemented.** Hardware sqrt was not added. The threshold is in accumulated integer units, not normalized correlation units. For variable-amplitude audio this is a real limitation: the threshold must be calibrated per session rather than using a universal value in [-1, 1]. A CORDIC sqrt unit would fix this but adds pipeline stages and area.

**N=64 reduction not attempted.** Reducing N from 128 to 64 was noted in M3 as a plan for M4, intended to cut cell count and ease routing. After confirming that DRT-0349 is a PDK-level rule issue unrelated to congestion, the N=64 change would not have fixed routing. It was not pursued.

**Python baseline is not competitive.** The speedup comparison is hardware vs. interpreted Python float32, not hardware vs. a well-optimized software implementation. This makes the 3.16x throughput speedup look smaller than it is for energy (700x) and larger than it would look against a NumPy or C baseline. The M1 assignment fixed the baseline at the Python implementation, so it is used as specified.
