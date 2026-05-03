# ECE 410/510 — Hardware for AI and Machine Learning
**Spring 2026 | Portland State University | Saleh Sabti**

## Project: Echo Detection Chiplet

A fixed-function chiplet that detects echoes in a phone call in real time. It takes two audio streams: the speaker output (far-end reference) and the mic input (near-end), computes their cross-correlation over a 128-sample window, and outputs one bit: echo present or not. No CPU in the detection path.

All 128 multiply-accumulate operations across a window are independent and fire in the same clock cycle. On-chip shift registers hold both sample buffers, so no DRAM traffic. The software baseline sits at 0.747 FLOP/byte (memory-bound on CPU). The chiplet flips that: compute-bound at 128 GFLOP/s peak against a 0.25 FLOP/byte ridge point.

**Interface: AXI4-Stream.** Required throughput is 0.064 MB/s at 16 kHz stereo INT16. AXI4-Stream is rated at 400 MB/s: 6250x headroom, never the bottleneck.

**Precision: INT16.** Full 16-bit codec dynamic range (96 dB SNR). INT8 loses 48 dB and degrades detection under low-SNR conditions. FP32 doubles byte traffic with no benefit since inputs are already quantized at the ADC.

## Repo Structure

```
codefest/
  cf01/                         CMAN hand calcs, ResNet-18 profiling
  cf02/                         CMAN roofline, cProfile, partition rationale
  cf03/                         GEMM CUDA kernels, roofline, COPT GPU forward pass
  cf04/                         INT8 quantization, MAC HDL (LLM A/B + correct), cocotb tests
  cf05/                         Systolic array trace (CMAN, due May 3)

project/
  heilmeier.md                  Heilmeier Q1-Q3, data-grounded
  echo_detect.py                Software baseline — pure Python, explicit MAC loop
  roofline_plot.py / roofline.png
  algorithm_diagram.png
  m1/
    sw_baseline.md              Intel Core Ultra 7 155H, median 260ms over 10 runs
    interface_selection.md      AXI4-Stream selection and bandwidth justification
    system_diagram.png          Host + interface + chiplet block diagram
  m2/
    rtl/
      compute_core.sv           Synthesizable compute core — parallel MAC tree, INT16, 40-bit acc
      interface.sv              AXI4-Stream slave (module: axi4s_rx)
    tb/
      tb_compute_core.sv        2/2 PASS
      tb_interface.sv           4/4 PASS
    sim/
      compute_core_run.log      Simulation transcript
      interface_run.log         Simulation transcript
      waveform.png              7-signal annotated waveform
    precision.md                INT16 rationale, overflow analysis, error analysis, roofline tie-in
    README.md                   Reproduction instructions

smoke_test/
  adder4.v / adder4_tb.v       LLM smoke test — 4-bit adder
```

## Running M2 Simulations

Requires Icarus Verilog 12.0. Run from repo root:

```bash
iverilog -g2012 -o /tmp/cc_sim project/m2/rtl/compute_core.sv project/m2/tb/tb_compute_core.sv
vvp /tmp/cc_sim

iverilog -g2012 -o /tmp/if_sim project/m2/rtl/interface.sv project/m2/tb/tb_interface.sv
vvp /tmp/if_sim
```

## Milestones

| Milestone | Due | Status |
|-----------|-----|--------|
| CF1 | Apr 5 | Done |
| CF2 + M1 | Apr 12 | Done |
| CF3 | Apr 19 | Done |
| CF4 | Apr 27 | Done |
| CF5 + M2 | May 3 | M2 done / CF5 CMAN in progress |
| M3 | May 24 | Not started |
| M4 | Jun 7 | Not started |
