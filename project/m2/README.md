# M2 — Echo Detection Chiplet: RTL and Testbenches

## Simulator

Icarus Verilog 12.0 (iverilog / vvp)

```bash
iverilog --version   # should print: Icarus Verilog version 12.0
```

## Reproducing the Simulations

Run from the repo root:

```bash
# Compute core
iverilog -g2012 -o /tmp/cc_sim \
  project/m2/rtl/compute_core.sv \
  project/m2/tb/tb_compute_core.sv
vvp /tmp/cc_sim

# Interface module
iverilog -g2012 -o /tmp/if_sim \
  project/m2/rtl/interface.sv \
  project/m2/tb/tb_interface.sv
vvp /tmp/if_sim
```

Expected output for both: last line printed is `PASS ...`.

VCD files are written to `project/m2/sim/` relative to the working directory. Run from repo root or adjust `$dumpfile` paths in the testbenches.

## Module Overview

### `compute_core.sv` — module `compute_core`

Computes unnormalized cross-correlation over a sliding N=128 sample window. Outputs `echo_det=1` when `acc_cross >= threshold`. INT16 inputs, 40-bit signed accumulators.

Latency: N+1 valid_in cycles after reset before the first valid output.

### `interface.sv` — module `axi4s_rx`

Note: `interface` is a reserved keyword in SystemVerilog; the module is named `axi4s_rx`. File is named `interface.sv` per M2 spec.

AXI4-Stream slave. TREADY is wired high (no back-pressure; required data rate is 0.064 MB/s vs. AXI4-S rated 400 MB/s). TDATA[31:16] = ref sample, TDATA[15:0] = mic sample. Outputs decoded pair to compute_core with 1-cycle latency.

## Deviations from M1

None. Interface remains AXI4-Stream as selected in `project/m1/interface_selection.md`.

## Python dependencies (waveform generation only)

```
matplotlib>=3.5
```

The simulation logs and waveform are already committed; re-running the waveform script is not required for grading.
