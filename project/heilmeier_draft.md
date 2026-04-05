# Heilmeier Draft
ECE 410/510 Spring 2026 | Saleh Sabti

## What I'm building

A hardware chiplet that takes two audio streams (far-end reference and near-end mic) and outputs one bit: echo present or not. No CPU in the detection path.

## How it works today and why that's a problem

Echo detection runs in software on a CPU or DSP, usually LMS or NLMS adaptive filters, sometimes a small classifier on top.

Three things break down. Latency: software detection adds milliseconds of delay that's audible on a live call. CPU load: the detection loop competes with other audio tasks and causes jitter under load. Power: keeping a CPU core alive for correlation burns far more than a dedicated circuit, which matters for earbuds and hearing aids on a battery budget.

## Why hardware works here

The chiplet computes normalized cross-correlation between the two signals and compares it to a threshold. That's the whole computation.

Every window is the same operation: dot product, normalization, compare. No branching, no variable-length inputs, no shifting memory access patterns. That's the profile custom silicon handles well. All N multiply-accumulate operations in a window are independent and fire in the same clock cycle. Keeping the sample buffers in on-chip shift registers removes DRAM traffic. The software baseline runs at 0.747 FLOP/byte (memory-bound). The hardware version isn't.
