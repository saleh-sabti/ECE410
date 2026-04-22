# ECE 410/510 — Hardware for AI and Machine Learning
**Spring 2026 | Portland State University | Saleh Sabti**

## Project: Echo Detection Chiplet

A fixed-function chiplet that computes normalized cross-correlation between a far-end reference signal and a near-end mic signal and outputs one bit: echo present or not. No CPU in the detection path.

Every window is the same operation: dot product, normalization, compare. That makes it a good fit for custom silicon. All N MACs in a window are independent and fire in the same clock cycle. On-chip shift registers hold the sample buffers, eliminating DRAM traffic. The software baseline runs at 0.747 FLOP/byte (memory-bound). The hardware version runs at 0.747 FLOP/byte against a 0.25 ridge — compute-bound.

## HDL Compute Core

`project/hdl/echo_detect_core.sv` implements the top-level compute module for the chiplet. It takes one INT16 sample pair per cycle (ref, mic), maintains N=128 shift registers on-chip, and accumulates the three dot products needed for normalized cross-correlation. Output is a 1-bit echo detection flag.

**Precision: INT16.** Audio samples from a 16-bit DAC/ADC sit in the range [-32768, 32767]. INT8 would lose 8 bits of dynamic range, introducing quantization noise that pushes the correlation threshold uncertainty above acceptable limits for echo detection. INT16 preserves full codec precision with no off-chip quantization step.

**Interface: AXI4 Stream.** The M1 arithmetic intensity analysis found the chiplet needs 0.064 MB/s of sample throughput at 16 kHz, 16-bit stereo (ref + mic). AXI4 Stream rated at 400 MB/s gives a 6250x headroom margin, so the interface is never the bottleneck. AXI4 Stream is also the natural fit for sample-at-a-time streaming: no addressing overhead, built-in flow control via TVALID/TREADY, and direct path into the on-chip shift registers without buffering.

## Repo Structure

```
codefest/
  cf01/                         Codefest 1 — CMAN hand calcs, ResNet-18 profiling
  cf02/                         Codefest 2 — CMAN roofline, cProfile, partition rationale
  cf03/                         Codefest 3 — GEMM CUDA kernels, roofline, COPT GPU forward pass
  cf04/
    hdl/
      mac_llm_A.v               Claude Sonnet 4.6 MAC output
      mac_llm_B.v               GPT-4o MAC output (pending)
      mac_tb.v                  Verilog testbench
      mac_correct.v             Corrected implementation
    review/
      mac_code_review.md        LLM comparison and issue analysis
    cocotb_mac/
      test_mac.py               cocotb testbench (basic + overflow)
      Makefile                  cocotb + icarus build
    cman_quantization.md        INT8 symmetric quantization (hand-computed)

project/
  heilmeier.md                  Heilmeier Q1-Q3, data-grounded
  algorithm_diagram.png         Block diagram (from CF1)
  echo_detect.py                Software baseline — pure Python, explicit MAC loop
  roofline_plot.py              Roofline plot script
  hdl/
    echo_detect_core.sv         Top-level compute core, N=128, INT16, parameterized
  m1/
    sw_baseline.md              Platform, median 260ms, throughput, memory
    interface_selection.md      AXI4 Stream — bandwidth calc and justification
    system_diagram.png          High-level system block diagram

smoke_test/
  adder4.v / adder4_tb.v       LLM smoke test — 4-bit adder in Verilog
```

## Milestones

| Milestone | Due | Status |
|-----------|-----|--------|
| Codefest 1 | Apr 5 | Done |
| Codefest 2 + M1 | Apr 12 | Done |
| Codefest 3 | Apr 19 | Done |
| Codefest 4 | Apr 27 | In progress |
| M2 | May 3 | Not started |
| M3 | May 24 | Not started |
| M4 | Jun 7 | Not started |
