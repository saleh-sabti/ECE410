# ECE 410/510 — Hardware for AI and Machine Learning
**Spring 2026 | Portland State University | Saleh Sabti**

## Project: Echo Detection Chiplet

A fixed-function chiplet that computes normalized cross-correlation between a far-end reference signal and a near-end mic signal and outputs one bit: echo present or not. No CPU in the detection path.

Every window is the same operation: dot product, normalization, compare. That makes it a good fit for custom silicon. All N MACs in a window are independent and fire in the same clock cycle. On-chip shift registers hold the sample buffers, eliminating DRAM traffic. The software baseline runs at 0.747 FLOP/byte (memory-bound). The hardware version runs at 0.747 FLOP/byte against a 0.25 ridge — compute-bound.

## Repo Structure

```
codefest/
  cf01/                         Codefest 1 — CMAN hand calcs, ResNet-18 profiling
  cf02/
    cman_roofline.md            CMAN — roofline construction, GEMM + vector-add kernels
    image.png                   Hand-drawn roofline diagram
    profiling/
      project_profile.txt       cProfile output, 10 runs
      roofline_project.png      Roofline — SW point + HW design point
    analysis/
      ai_calculation.md         FLOPs derivation, bytes, AI = 0.747 FLOP/byte
      partition_rationale.md    HW/SW partition, all 4 sub-questions

project/
  heilmeier.md                  Heilmeier Q1-Q3, data-grounded
  algorithm_diagram.png         Block diagram (from CF1)
  echo_detect.py                Software baseline — pure Python, explicit MAC loop
  roofline_plot.py              Roofline plot script
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
| M2 | May 3 | Not started |
| M3 | May 24 | Not started |
| M4 | Jun 7 | Not started |
