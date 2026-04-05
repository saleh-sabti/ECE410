# ECE 410/510 — Hardware for AI and Machine Learning
**Spring 2026 | Portland State University | Saleh Sabti**

## Project: Echo Detection Chiplet

A fixed-function chiplet that computes normalized cross-correlation between a far-end reference signal and a near-end mic signal and outputs one bit: echo present or not. No CPU in the detection path.

Every window is the same operation: dot product, normalization, compare. That makes it a good fit for custom silicon. All N MACs in a window are independent and fire in the same clock cycle. On-chip shift registers hold the sample buffers, eliminating DRAM traffic. The software baseline runs at 0.747 FLOP/byte (memory-bound). The hardware version isn't.

## Repo Structure

```
codefest/cf01/          Codefest 1 - CMAN hand calcs, ResNet-18 profiling
project/                Heilmeier draft, algorithm diagram, Python baseline
smoke_test/             LLM smoke test - 4-bit adder in Verilog
```

## Milestones

| Milestone | Due | Status |
|-----------|-----|--------|
| Codefest 1 | Apr 5 | Done |
| M1 | Apr 12 | In progress |
| M2 | May 3 | Not started |
| M3 | May 24 | Not started |
| M4 | Jun 7 | Not started |
